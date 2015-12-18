from django.db.models import Sum, F

from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_prev_cycle
from dashboard.helpers import STABLE_CONSUMPTION, NOT_REPORTING, NO, YES, F3, F2, F1
from dashboard.models import Cycle, Consumption

SUM = 'sum'

THRESHOLD = "threshold"

CONSUMPTION_QUERY = "consumption_query"

PMTCT_CONSUMPTION = 'pmtct_consumption'

ART_CONSUMPTION = 'art_consumption'


class StableConsumption(CycleFormulationCheck):
    test = STABLE_CONSUMPTION

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {"name": F1, CONSUMPTION_QUERY: "Efavirenz (TDF/3TC/EFV)", THRESHOLD: 20},
            {"name": F2, CONSUMPTION_QUERY: "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]", THRESHOLD: 10},
            {"name": F3, CONSUMPTION_QUERY: "(EFV) 200mg [Pack 90]", THRESHOLD: 10}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            threshold = formulation[THRESHOLD]
            qs = Cycle.objects.filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                try:
                    next_cycle_qs = Consumption.objects.annotate(consumption=Sum(F(ART_CONSUMPTION) + F(PMTCT_CONSUMPTION))).filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY], consumption__gte=threshold)
                    current_cycle_qs = Consumption.objects.annotate(consumption=Sum(F(ART_CONSUMPTION) + F(PMTCT_CONSUMPTION))).filter(facility_cycle__facility=record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=formulation[CONSUMPTION_QUERY], consumption__gte=threshold)
                    number_of_consumption_records = current_cycle_qs.count()
                    number_of_consumption_records_next_cycle = next_cycle_qs.count()
                    next_cycle_consumption = next_cycle_qs.aggregate(sum=Sum(F(ART_CONSUMPTION) + F(PMTCT_CONSUMPTION))).get(SUM, 0)
                    current_cycle_consumption = current_cycle_qs.aggregate(sum=Sum(F(ART_CONSUMPTION) + F(PMTCT_CONSUMPTION))).get(SUM, 0)
                    result = NOT_REPORTING
                    if number_of_consumption_records == 0 or number_of_consumption_records_next_cycle == 0:
                        not_reporting += 1
                    elif 0.5 < (next_cycle_consumption / current_cycle_consumption) < 1.5:
                        yes += 1
                        result = YES
                    else:
                        no += 1
                        result = NO
                except TypeError as e:
                    no += 1
                    result = NO
                finally:
                    self.record_result_for_facility(record, result, formulation["name"])
            self.build_cycle_formulation_score(cycle, formulation["name"], yes, no, not_reporting, total_count)
