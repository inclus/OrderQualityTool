from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import to_date, format_range, DIFFERENT_ORDERS_OVER_TIME, NOT_REPORTING, YES, NO, F3, F2, F1
from dashboard.models import Cycle, Consumption

PATIENTS = 'estimated_number_of_new_patients'

ART_CONSUMPTION = 'art_consumption'

BALANCE = 'opening_balance'


def get_prev_cycle(cycle):
    current_cycle_date = to_date(cycle)
    start_month = current_cycle_date.replace(months=-3)
    end_month = current_cycle_date.replace(months=-2)
    prev_cycle = format_range(start_month, end_month)
    return prev_cycle


class DifferentOrdersOverTime(CycleFormulationCheck):
    test = DIFFERENT_ORDERS_OVER_TIME
    F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
    F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
    F3_QUERY = "EFV) 200mg [Pack 90]"

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)

        formulations = [
            {"name": F1, "consumption_query": self.F1_QUERY},
            {"name": F2, "consumption_query": self.F2_QUERY},
            {"name": F3, "consumption_query": self.F3_QUERY}
        ]
        for formulation in formulations:
            query = formulation["consumption_query"]
            actual_name = formulation['name']
            no = 0
            yes = 0
            not_reporting = 0
            total_count = Cycle.objects.filter(cycle=cycle).count()

            for facility_record in Cycle.objects.filter(cycle=cycle):
                current_values = Consumption.objects.filter(facility_cycle=facility_record, formulation__icontains=query).order_by().values(BALANCE, ART_CONSUMPTION, PATIENTS)
                prev_values = Consumption.objects.filter(facility_cycle__facility=facility_record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=query).order_by().values(BALANCE, ART_CONSUMPTION, PATIENTS)
                result = NOT_REPORTING
                if len(prev_values) == 0 or len(current_values) == 0:
                    not_reporting += 1
                else:
                    no, result, yes = self.compare_values(prev_values, current_values, no, result, yes)
                self.record_result_for_facility(facility_record, result, actual_name)
            self.build_cycle_formulation_score(cycle, actual_name, yes, no, not_reporting, total_count)

    def compare_values(self, prev_values, current_values, no, result, yes):
        # yes if all are 0
        # yes if any does not match the new ones
        # no if all same
        # no if
        current_balance = current_values[0].get(BALANCE)
        current_art_consumption = current_values[0].get(ART_CONSUMPTION)
        current_patients = current_values[0].get(PATIENTS)

        prev_balance = prev_values[0].get(BALANCE)
        prev_art_consumption = prev_values[0].get(ART_CONSUMPTION)
        prev_patients = prev_values[0].get(PATIENTS)

        if current_balance != 0 and current_balance == prev_balance and current_art_consumption == prev_art_consumption and prev_patients == current_patients:
            no += 1
            result = NO
        else:
            yes += 1
            result = YES
        return no, result, yes
