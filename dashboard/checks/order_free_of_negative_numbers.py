import operator

from django.db.models import Q

from dashboard.checks.common import Check
from dashboard.helpers import ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, NOT_REPORTING, NO, YES, F3, F2, F1
from dashboard.models import Consumption, Cycle, CycleFormulationScore


class OrderFormFreeOfNegativeNumbers(Check):
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS

    def run(self, cycle):
        formulations = [
            {"name": F1, "consumption_query": "Efavirenz (TDF/3TC/EFV)"},
            {"name": F2, "consumption_query": "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
            {"name": F3, "consumption_query": "EFV) 200mg [Pack 90]"}
        ]
        for formulation in formulations:
            query = formulation["consumption_query"]
            actual_name = formulation['name']
            filter_list = [Q(opening_balance__lt=0), Q(quantity_received__lt=0), Q(pmtct_consumption__lt=0), Q(art_consumption__lt=0), Q(estimated_number_of_new_pregnant_women__lt=0), Q(total_quantity_to_be_ordered__lt=0)]
            total_count = Cycle.objects.filter(cycle=cycle).count()
            not_reporting = 0
            yes = 0
            no = 0
            for record in Cycle.objects.filter(cycle=cycle):
                number_of_records = Consumption.objects.filter(facility_cycle=record, formulation__icontains=query).count()
                number_of_valid_records = Consumption.objects.filter(facility_cycle__cycle=cycle, formulation__icontains=query).exclude(reduce(operator.or_, filter_list)).count()
                result = NOT_REPORTING
                if number_of_records == 0 or not record.reporting_status:
                    not_reporting += 1
                elif number_of_valid_records > 0:
                    no += 1
                    result = NO
                else:
                    yes += 1
                    result = YES
                self.record_result_for_facility(record, result, actual_name)

            score, _ = CycleFormulationScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, formulation=actual_name)
            yes_rate = float(yes * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = float(no * 100) / float(total_count)
            score.not_reporting = not_reporting_rate
            score.save()
