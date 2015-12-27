from django.db.models import Count, Case, When

from dashboard.checks.common import Check
from dashboard.helpers import ORDER_FORM_FREE_OF_GAPS, NOT_REPORTING, NO, YES
from dashboard.models import Cycle, CycleScore, Consumption, AdultPatientsRecord, PAEDPatientsRecord


class OrderFormFreeOfGaps(Check):
    test = ORDER_FORM_FREE_OF_GAPS

    def run(self, cycle):
        yes = 0
        no = 0
        not_reporting = 0
        number_of_facilities = Cycle.objects.filter(cycle=cycle).count()
        data = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle).annotate(
                number_facility_consumption_records=Count('consumption', distinct=True),
                number_of_adult_records=Count('ads', distinct=True),
                number_of_paed_records=Count('pds', distinct=True)
        )
        for record in data:
            con_blank_count = Consumption.objects.filter(facility_cycle=record).aggregate(
                    number_of_blanks_f1=Count(Case(When(opening_balance__isnull=True, then=1))),
                    number_of_blanks_f2=Count(Case(When(quantity_received__isnull=True, then=1))),
                    number_of_blanks_f3=Count(Case(When(art_consumption__isnull=True, then=1))),
                    number_of_blanks_f4=Count(Case(When(loses_adjustments__isnull=True, then=1))),
                    number_of_blanks_f5=Count(Case(When(estimated_number_of_new_patients__isnull=True, then=1))),
                    total_count=Count('pk')
            )
            adult_blank_count = AdultPatientsRecord.objects.filter(facility_cycle=record).aggregate(
                    number_of_blanks_f6=Count(Case(When(new__isnull=True, then=1))),
                    number_of_blanks_f7=Count(Case(When(existing__isnull=True, then=1))),
                    total_count=Count('pk')
            )

            paed_blank_count = PAEDPatientsRecord.objects.filter(facility_cycle=record).aggregate(
                    number_of_blanks_f8=Count(Case(When(new__isnull=True, then=1))),
                    number_of_blanks_f9=Count(Case(When(existing__isnull=True, then=1))),
                    total_count=Count('pk')
            )
            blank_counts = [
                con_blank_count['number_of_blanks_f1'],
                con_blank_count['number_of_blanks_f2'],
                con_blank_count['number_of_blanks_f3'],
                con_blank_count['number_of_blanks_f4'],
                con_blank_count['number_of_blanks_f5'],
                adult_blank_count['number_of_blanks_f6'],
                adult_blank_count['number_of_blanks_f7'],
                paed_blank_count['number_of_blanks_f8'],
                paed_blank_count['number_of_blanks_f9'],
            ]
            number_of_consumption_records = con_blank_count['total_count']
            number_of_adult_records = adult_blank_count['total_count']
            number_of_paed_records = paed_blank_count['total_count']
            number_of_blanks = sum(blank_counts)
            no, not_reporting, yes, score = self.process_facility(no, not_reporting, yes, number_of_blanks, number_of_consumption_records, number_of_adult_records, number_of_paed_records)
            self.record_result_for_facility(record, score, test=self.test)

        yes_rate = float(yes) * 100 / float(number_of_facilities)
        not_rate = float(no) * 100 / float(number_of_facilities)
        not_reporting_rate = float(not_reporting) * 100 / float(number_of_facilities)
        score, _ = CycleScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_GAPS)
        score.yes = yes_rate
        score.no = not_rate
        score.not_reporting = not_reporting_rate
        score.save()
        return score

    def process_facility(self, no, not_reporting, yes, number_of_blanks, number_of_consumption_records, number_of_adult_records, number_of_paed_records):
        score = NOT_REPORTING
        if number_of_consumption_records >= 25 and number_of_adult_records >= 22 and number_of_paed_records >= 7 and number_of_blanks <= 2:
            yes += 1
            score = YES
        elif number_of_consumption_records > 0 or number_of_adult_records > 0 or number_of_paed_records > 0:
            no += 1
            score = NO
        elif number_of_consumption_records == 0 and number_of_adult_records == 0 and number_of_paed_records == 0:
            not_reporting += 1
        return no, not_reporting, yes, score
