import operator

from django.db.models import Q

from dashboard.checks.common import Check
from dashboard.helpers import ADULT, PAED, ORDER_FORM_FREE_OF_GAPS
from dashboard.models import FacilityConsumptionRecord, AdultPatientsRecord, PAEDPatientsRecord, FacilityCycleRecord, CONSUMPTION, CycleTestScore


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
        filter_list = [Q(opening_balance=None), Q(quantity_received=None), Q(pmtct_consumption=None), Q(art_consumption=None), Q(loses_adjustments=None), Q(closing_balance=None), Q(months_of_stock_of_hand=None), Q(quantity_required_for_current_patients=None), Q(estimated_number_of_new_patients=None), Q(estimated_number_of_new_pregnant_women=None), Q(total_quantity_to_be_ordered=None)]
        data = FacilityConsumptionRecord.objects.filter(facility_cycle__cycle=cycle).exclude(reduce(operator.or_, filter_list)).values('facility_cycle__facility__name').annotate(count=Count('pk'))
        adult_data = AdultPatientsRecord.objects.filter(facility_cycle__cycle=cycle).exclude(Q(new=None) | Q(existing=None)).values('facility_cycle__facility__name').annotate(count=Count('pk'))
        paed_data = PAEDPatientsRecord.objects.filter(facility_cycle__cycle=cycle).exclude(Q(new=None) | Q(existing=None)).values('facility_cycle__facility__name').annotate(count=Count('pk'))
        data_as_dict = dict((value['facility_cycle__facility__name'], value["count"]) for value in data)
        adult_data_as_dict = dict((value['facility_cycle__facility__name'], value["count"]) for value in adult_data)
        paed_data_as_dict = dict((value['facility_cycle__facility__name'], value["count"]) for value in paed_data)
        combined_data = list()
        for record in FacilityCycleRecord.objects.filter(cycle=cycle):
            name = record.facility.name
            item = {}
            if name in data_as_dict:
                item[CONSUMPTION] = data_as_dict[name]

            if name in adult_data_as_dict:
                item[ADULT] = adult_data_as_dict[name]

            if name in paed_data_as_dict:
                item[PAED] = paed_data_as_dict[name]
            combined_data.append(item)

        yes, no, not_reporting, count = reduce(calculate_rate, combined_data, [0, 0, 0, 0])
        yes_rate = float(yes) * 100 / float(count)
        not_rate = float(no) * 100 / float(count)
        not_reporting_rate = float(not_reporting) * 100 / float(count)
        score, _ = CycleTestScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_GAPS)
        score.yes = yes_rate
        score.no = not_rate
        score.not_reporting = not_reporting_rate
        score.save()
        return score
