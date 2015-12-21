from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_prev_cycle
from dashboard.helpers import CLOSING_BALANCE_MATCHES_OPENING_BALANCE, NOT_REPORTING, YES, NO, F3, F2, F1
from dashboard.models import Consumption, Cycle

CONSUMPTION_QUERY = "consumption_query"

NAME = "name"


class ClosingBalance(CycleFormulationCheck):
    test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE
    F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
    F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
    F3_QUERY = "EFV) 200mg [Pack 90]"

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {NAME: F1, CONSUMPTION_QUERY: self.F1_QUERY},
            {NAME: F2, CONSUMPTION_QUERY: self.F2_QUERY},
            {NAME: F3, CONSUMPTION_QUERY: self.F3_QUERY}
        ]
        for formulation in formulations:
            query = formulation[CONSUMPTION_QUERY]
            actual_name = formulation[NAME]
            no = 0
            yes = 0
            not_reporting = 0
            total_count = Cycle.objects.filter(cycle=cycle).count()
            for facility_record in Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle):
                new_values = self.get_values_for_previous_cycle(facility_record, query)
                current_values = self.get_values_for_current_cycle(facility_record, prev_cycle, query)
                result = NOT_REPORTING
                if self.has_no_valid_values(current_values, facility_record, new_values):
                    not_reporting += 1
                else:
                    no, result, yes = self.compare_values(current_values, new_values, no, result, yes)
                self.record_result_for_facility(facility_record, result, actual_name)
            self.build_cycle_formulation_score(cycle, actual_name, yes, no, not_reporting, total_count)

    def compare_values(self, current_values, new_values, no, result, yes):
        combined_list = current_values[0].values() + new_values[0].values()
        diff = list(set(new_values[0].values()) - set(current_values[0].values()))
        if len(diff) > 0 or None in combined_list:
            no += 1
            result = NO
        else:
            yes += 1
            result = YES
        return no, result, yes

    def has_no_valid_values(self, current_values, facility_record, new_values):
        return len(current_values) == 0 or len(new_values) == 0

    def get_values_for_previous_cycle(self, facility_record, query):
        return Consumption.objects.filter(facility_cycle=facility_record, formulation__icontains=query).order_by().values('opening_balance')

    def get_values_for_current_cycle(self, facility_record, prev_cycle, query):
        return Consumption.objects.filter(facility_cycle__facility=facility_record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=query).order_by().values('closing_balance')
