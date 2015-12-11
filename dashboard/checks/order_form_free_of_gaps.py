import functools
import operator

from django.db.models import Q

from dashboard.checks.common import Check
from dashboard.helpers import ORDER_FORM_FREE_OF_GAPS, NOT_REPORTING, NO, YES
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord, AdultPatientsRecord, PAEDPatientsRecord, CycleTestScore, FacilityCycleRecordScore


class OrderFormFreeOfGaps(Check):
    test = ORDER_FORM_FREE_OF_GAPS
    def run(self, cycle):
        filter_list = [Q(opening_balance__isnull=True), Q(quantity_received__isnull=True), Q(art_consumption__isnull=True), Q(loses_adjustments__isnull=True), Q(estimated_number_of_new_patients__isnull=True)]
        yes = 0
        no = 0
        not_reporting = 0
        number_of_facilities = FacilityCycleRecord.objects.filter(cycle=cycle).count()
        for facilityCycleRecord in FacilityCycleRecord.objects.filter(cycle=cycle):
            no, not_reporting, yes = self.process_facility(facilityCycleRecord, filter_list, no, not_reporting, yes)

        yes_rate = float(yes) * 100 / float(number_of_facilities)
        not_rate = float(no) * 100 / float(number_of_facilities)
        not_reporting_rate = float(not_reporting) * 100 / float(number_of_facilities)
        score, _ = CycleTestScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_GAPS)
        score.yes = yes_rate
        score.no = not_rate
        score.not_reporting = not_reporting_rate
        score.save()
        return score

    def process_facility(self, facilityCycleRecord, filter_list, no, not_reporting, yes):
        number_of_records_for_facility = FacilityConsumptionRecord.objects.filter(facility_cycle=facilityCycleRecord).count()
        score = NOT_REPORTING
        if number_of_records_for_facility == 0:
            not_reporting += 1
        else:
            number_facility_consumption_records = FacilityConsumptionRecord.objects.filter(facility_cycle=facilityCycleRecord).exclude(functools.reduce(operator.or_, filter_list)).count()
            number_of_adult_records = AdultPatientsRecord.objects.filter(facility_cycle=facilityCycleRecord).exclude(Q(new__isnull=True) | Q(existing__isnull=True)).count()
            number_of_paed_records = PAEDPatientsRecord.objects.filter(facility_cycle=facilityCycleRecord).exclude(Q(new__isnull=True) | Q(existing__isnull=True)).count()
            if number_facility_consumption_records >= 24 and number_of_adult_records >= 22 and number_of_paed_records >= 7:
                yes += 1
                score = YES
            else:
                no += 1
                score = NO
        score_record, _ = FacilityCycleRecordScore.objects.get_or_create(facility_cycle=facilityCycleRecord, test=ORDER_FORM_FREE_OF_GAPS)
        score_record.score = score
        score_record.save()
        return no, not_reporting, yes
