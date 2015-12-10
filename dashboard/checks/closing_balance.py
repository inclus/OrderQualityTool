from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_next_cycle
from dashboard.helpers import CLOSING_BALANCE_MATCHES_OPENING_BALANCE
from dashboard.models import FacilityConsumptionRecord, FacilityCycleRecord


class ClosingBalance(CycleFormulationCheck):
    test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE

    def run(self, cycle):
        next_cycle = get_next_cycle(cycle)
        formulations = [
            {"name": "TDF/3TC/EFV (Adult)", "consumption_query": "Efavirenz (TDF/3TC/EFV)"},
            {"name": "ABC/3TC (Paed)", "consumption_query": "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
            {"name": "EFV200 (Paed)", "consumption_query": "EFV) 200mg [Pack 90]"}
        ]
        for formulation in formulations:
            name = formulation["consumption_query"]
            no = 0
            yes = 0
            not_reporting = 0
            total_count = FacilityCycleRecord.objects.filter(cycle=cycle).count()
            for facility_record in FacilityCycleRecord.objects.filter(cycle=cycle):
                current_values = FacilityConsumptionRecord.objects.filter(facility_cycle=facility_record, formulation__icontains=name).order_by().values('closing_balance')
                new_values = FacilityConsumptionRecord.objects.filter(facility_cycle__facility=facility_record.facility, facility_cycle__cycle=next_cycle, formulation__icontains=name).order_by().values('opening_balance')
                if len(current_values) == 0 or len(new_values) == 0 or not facility_record.reporting_status:
                    not_reporting += 1
                else:
                    combined_list = current_values[0].values() + new_values[0].values()
                    diff = list(set(new_values[0].values()) - set(current_values[0].values()))
                    if len(diff) > 1 or None in combined_list:
                        no += 1
                    else:
                        yes += 1
            self.build_cycle_formulation_score(cycle, name, yes, no, not_reporting, total_count)
