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

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {NAME: F1, CONSUMPTION_QUERY: "Efavirenz (TDF/3TC/EFV)"},
            {NAME: F2, CONSUMPTION_QUERY: "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
            {NAME: F3, CONSUMPTION_QUERY: "(EFV) 200mg [Pack 90]"}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            qs = Cycle.objects.filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                try:
                    next_cycle_qs = Consumption.objects.annotate(consumption=Sum(PACKS_ORDERED)).filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY])
                    current_cycle_qs = Consumption.objects.annotate(consumption=Sum(QUANTITY_RECEIVED)).filter(facility_cycle__facility=record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=formulation[CONSUMPTION_QUERY])
                    number_of_consumption_records = current_cycle_qs.count()
                    number_of_consumption_records_next_cycle = next_cycle_qs.count()
                    amount_received = next_cycle_qs.aggregate(sum=Sum(QUANTITY_RECEIVED)).get(SUM, 0)
                    amount_ordered = current_cycle_qs.aggregate(sum=Sum(PACKS_ORDERED)).get(SUM, 0)
                    result = NOT_REPORTING
                    if number_of_consumption_records == 0 or number_of_consumption_records_next_cycle == 0:
                        not_reporting += 1
                    elif amount_ordered == amount_received:
                        yes += 1
                        result = YES
                    else:
                        no += 1
                        result = NO
                except TypeError as e:
                    no += 1
                    result = NO
                finally:
                    self.record_result_for_facility(record, result, formulation[NAME])

            self.build_cycle_formulation_score(cycle, formulation[NAME], yes, no, not_reporting, total_count)
