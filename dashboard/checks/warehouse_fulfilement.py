from django.db.models import Sum

from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_prev_cycle
from dashboard.helpers import WAREHOUSE_FULFILMENT, NOT_REPORTING, YES, NO, F3, F2, F1
from dashboard.models import Cycle, Consumption

NAME = 'name'

QUANTITY_RECEIVED = "quantity_received"

PACKS_ORDERED = "packs_ordered"

SUM = 'sum'

CONSUMPTION_QUERY = "consumption_query"


class WarehouseFulfilment(CycleFormulationCheck):
    test = WAREHOUSE_FULFILMENT
    F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
    F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
    F3_QUERY = "(EFV) 200mg [Pack 90]"

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {NAME: F1, CONSUMPTION_QUERY: self.F1_QUERY},
            {NAME: F2, CONSUMPTION_QUERY: self.F2_QUERY},
            {NAME: F3, CONSUMPTION_QUERY: self.F3_QUERY}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                current_qs = Consumption.objects.annotate(consumption=Sum(PACKS_ORDERED)).filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY])
                prev_qs = Consumption.objects.annotate(consumption=Sum(QUANTITY_RECEIVED)).filter(facility_cycle__facility=record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=formulation[CONSUMPTION_QUERY])
                number_of_consumption_records = prev_qs.count()
                number_of_consumption_records_next_cycle = current_qs.count()
                amount_received = current_qs.aggregate(sum=Sum(QUANTITY_RECEIVED)).get(SUM, 0)
                amount_ordered = prev_qs.aggregate(sum=Sum(PACKS_ORDERED)).get(SUM, 0)
                result = NOT_REPORTING
                if number_of_consumption_records == 0 or number_of_consumption_records_next_cycle == 0:
                    not_reporting += 1
                elif amount_ordered == amount_received:
                    yes += 1
                    result = YES
                else:
                    no += 1
                    result = NO
                self.record_result_for_facility(record, result, formulation[NAME])

            self.build_cycle_formulation_score(cycle, formulation[NAME], yes, no, not_reporting, total_count)
