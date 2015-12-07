from dashboard.checks.common import Check
from dashboard.checks.different_orders_over_time import get_next_cycle
from dashboard.helpers import CLOSING_BALANCE_MATCHES_OPENING_BALANCE
from dashboard.models import FacilityConsumptionRecord, FacilityCycleRecord, CycleFormulationTestScore


class ClosingBalance(Check):
    def run(self, cycle):
        next_cycle = get_next_cycle(cycle)
        formulation_values = FacilityConsumptionRecord.objects.filter(facility_cycle__cycle=cycle).order_by().values('formulation').distinct()
        for formulation in formulation_values:
            name = formulation["formulation"]
            no = 0
            yes = 0
            not_reporting = 0
            total_count = FacilityCycleRecord.objects.filter(cycle=cycle).count()
            for facility_record in FacilityCycleRecord.objects.filter(cycle=cycle):
                current_values = FacilityConsumptionRecord.objects.filter(facility_cycle=facility_record, formulation=name).order_by().values('closing_balance')
                new_values = FacilityConsumptionRecord.objects.filter(facility_cycle__facility=facility_record.facility, facility_cycle__cycle=next_cycle, formulation=name).order_by().values('opening_balance')
                if len(current_values) == 0 or len(new_values) == 0 or not facility_record.reporting_status:
                    not_reporting += 1
                else:
                    combined_list = current_values[0].values() + new_values[0].values()
                    diff = list(set(new_values[0].values()) - set(current_values[0].values()))
                    if len(diff) > 1 or None in combined_list:
                        no += 1
                    else:
                        yes += 1
            score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=CLOSING_BALANCE_MATCHES_OPENING_BALANCE, formulation=name)
            yes_rate = float(yes * 100) / float(total_count)
            no_rate = float(no * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = no_rate
            score.not_reporting = not_reporting_rate
            score.save()
