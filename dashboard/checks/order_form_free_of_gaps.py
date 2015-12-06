import operator

from django.db.models import Q

from dashboard.checks.common import Check
from dashboard.helpers import ADULT, PAED, ORDER_FORM_FREE_OF_GAPS
from dashboard.models import FacilityCycleRecord, CONSUMPTION, FacilityConsumptionRecord, AdultPatientsRecord, PAEDPatientsRecord, CycleTestScore


def calculate_rate(accumulator, item):
    if CONSUMPTION in item and ADULT in item and PAED in item:
        yes = 1 if item[CONSUMPTION] > 22 and item[ADULT] > 6 and item[PAED] > 4 else 0
        no = 1 if 0 < item[CONSUMPTION] < 23 and 0 < item[ADULT] < 6 and 0 < item[PAED] < 4 else 0
        not_reporting = 1 if item[CONSUMPTION] == 0 or item[ADULT] == 0 or item[PAED] == 4 else 0
    elif CONSUMPTION in item or ADULT in item or PAED in item:
        yes = 0
        no = 1
        not_reporting = 0
    else:
        yes = 0
        no = 0
        not_reporting = 1

    accumulator[0] += yes
    accumulator[1] += no
    accumulator[2] += not_reporting
    accumulator[3] += 1

    return accumulator


class OrderFormFreeOfGaps(Check):
    def run(self, cycle):
        filter_list = [Q(opening_balance=None), Q(quantity_received=None), Q(art_consumption=None), Q(loses_adjustments=None), Q(estimated_number_of_new_patients=None)]
        yes = 0
        no = 0
        not_reporting = 0
        number_of_facilities = FacilityCycleRecord.objects.count()
        for facilityCycleRecord in FacilityCycleRecord.objects.filter(cycle=cycle):
            number_of_records_for_facility = FacilityConsumptionRecord.objects.filter(facility_cycle=facilityCycleRecord).count()
            if number_of_records_for_facility == 0:
                not_reporting += 1
            else:
                number_facility_consumption_records = FacilityConsumptionRecord.objects.filter(facility_cycle=facilityCycleRecord).exclude(reduce(operator.or_, filter_list)).count()
                number_of_adult_records = AdultPatientsRecord.objects.filter(facility_cycle__cycle=cycle).exclude(Q(new=None) | Q(existing=None)).count()
                number_of_paed_records = PAEDPatientsRecord.objects.filter(facility_cycle__cycle=cycle).exclude(Q(new=None) | Q(existing=None)).count()

                if number_facility_consumption_records >= 25 and number_of_adult_records >= 22 and number_of_paed_records >= 7:
                    yes += 1
                else:
                    no += 1

        yes_rate = float(yes) * 100 / float(number_of_facilities)
        not_rate = float(no) * 100 / float(number_of_facilities)
        not_reporting_rate = float(not_reporting) * 100 / float(number_of_facilities)
        score, _ = CycleTestScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_GAPS)
        score.yes = yes_rate
        score.no = not_rate
        score.not_reporting = not_reporting_rate
        score.save()
        return score
