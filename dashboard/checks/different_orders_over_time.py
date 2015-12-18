from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import to_date, format_range, DIFFERENT_ORDERS_OVER_TIME, NOT_REPORTING, YES, NO, F3, F2, F1
from dashboard.models import Cycle, Consumption


def get_prev_cycle(cycle):
    current_cycle_date = to_date(cycle)
    start_month = current_cycle_date.replace(months=-3)
    end_month = current_cycle_date.replace(months=-2)
    prev_cycle = format_range(start_month, end_month)
    return prev_cycle


class DifferentOrdersOverTime(CycleFormulationCheck):
    test = DIFFERENT_ORDERS_OVER_TIME

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {"name": F1, "consumption_query": "Efavirenz (TDF/3TC/EFV)"},
            {"name": F2, "consumption_query": "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
            {"name": F3, "consumption_query": "EFV) 200mg [Pack 90]"}
        ]
        for formulation in formulations:
            query = formulation["consumption_query"]
            actual_name = formulation['name']
            no = 0
            yes = 0
            not_reporting = 0
            total_count = Cycle.objects.filter(cycle=cycle).count()

            for facility_record in Cycle.objects.filter(cycle=cycle):
                new_values = Consumption.objects.filter(facility_cycle=facility_record, formulation__icontains=query).order_by().values('opening_balance', 'art_consumption', 'estimated_number_of_new_patients')
                current_values = Consumption.objects.filter(facility_cycle__facility=facility_record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=query).order_by().values('opening_balance', 'art_consumption', 'estimated_number_of_new_patients')
                result = NOT_REPORTING
                if len(current_values) == 0 or len(new_values) == 0:
                    not_reporting += 1
                else:
                    combined_list = list(current_values[0].values()) + list(new_values[0].values())
                    diff = list(set(new_values[0].values()) - set(current_values[0].values()))
                    if len(diff) > 1 or None in combined_list:
                        no += 1
                        result = NO
                    else:
                        yes += 1
                        result = YES
                self.record_result_for_facility(facility_record, result, actual_name)
            self.build_cycle_formulation_score(cycle, actual_name, yes, no, not_reporting, total_count)
