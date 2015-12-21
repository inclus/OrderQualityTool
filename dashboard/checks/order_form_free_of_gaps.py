from django.db.models import Count, Case, When

from dashboard.checks.common import Check
from dashboard.helpers import ORDER_FORM_FREE_OF_GAPS, NOT_REPORTING, NO, YES
from dashboard.models import Cycle, CycleScore


class OrderFormFreeOfGaps(Check):
    test = ORDER_FORM_FREE_OF_GAPS

    def run(self, cycle):
        yes = 0
        no = 0
        not_reporting = 0
        number_of_facilities = Cycle.objects.filter(cycle=cycle).count()
        data = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle).annotate(
                count=Count("consumption__pk"),
                number_facility_consumption_records=Count(Case(
                        When(consumption__opening_balance__isnull=False, consumption__quantity_received__isnull=False, consumption__art_consumption__isnull=False, consumption__loses_adjustments__isnull=False, consumption__estimated_number_of_new_patients__isnull=False, then=1)
                )),
                number_of_adult_records=Count(Case(
                        When(ads__new__isnull=False, ads__existing__isnull=False, then=1)
                )),
                number_of_paed_records=Count(Case(
                        When(pds__new__isnull=False, pds__existing__isnull=False, then=1)
                )),

        )
        for facilityCycleRecord in data:
            no, not_reporting, yes = self.process_facility(facilityCycleRecord, no, not_reporting, yes)

        yes_rate = float(yes) * 100 / float(number_of_facilities)
        not_rate = float(no) * 100 / float(number_of_facilities)
        not_reporting_rate = float(not_reporting) * 100 / float(number_of_facilities)
        score, _ = CycleScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_GAPS)
        score.yes = yes_rate
        score.no = not_rate
        score.not_reporting = not_reporting_rate
        score.save()
        return score

    def process_facility(self, record, no, not_reporting, yes):
        number_of_records_for_facility = record.count
        score = NOT_REPORTING
        if number_of_records_for_facility == 0:
            not_reporting += 1
        else:
            if record.number_facility_consumption_records >= 24 and record.number_of_adult_records >= 22 and record.number_of_paed_records >= 7:
                yes += 1
                score = YES
            else:
                no += 1
                score = NO
        self.record_result_for_facility(record, score, test=ORDER_FORM_FREE_OF_GAPS)
        return no, not_reporting, yes
