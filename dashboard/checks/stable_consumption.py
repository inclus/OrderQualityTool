from django.db.models import Sum, F
from django.db.models.functions import Coalesce

from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_prev_cycle
from dashboard.helpers import STABLE_CONSUMPTION, NOT_REPORTING, NO, YES, F3, F2, F1
from dashboard.models import Cycle, Consumption

NAME = "name"

SUM = 'sum'

THRESHOLD = "threshold"

CONSUMPTION_QUERY = "consumption_query"

PMTCT_CONSUMPTION = 'pmtct_consumption'

ART_CONSUMPTION = 'art_consumption'


class StableConsumption(CycleFormulationCheck):
    test = STABLE_CONSUMPTION
    F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
    F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
    F3_QUERY = "(EFV) 200mg [Pack 90]"

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {NAME: F1, CONSUMPTION_QUERY: self.F1_QUERY, THRESHOLD: 20},
            {NAME: F2, CONSUMPTION_QUERY: self.F2_QUERY, THRESHOLD: 10},
            {NAME: F3, CONSUMPTION_QUERY: self.F3_QUERY, THRESHOLD: 10}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            threshold = formulation[THRESHOLD]
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle, reporting_status=True)
            total_count = Cycle.objects.filter(cycle=cycle).count()
            not_reporting = Cycle.objects.filter(cycle=cycle, reporting_status=False).count()
            for record in qs:
                result = NOT_REPORTING
                current_qs = Consumption.objects.filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY])
                prev_qs = Consumption.objects.filter(facility_cycle__facility=record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=formulation[CONSUMPTION_QUERY])
                number_of_consumption_records = prev_qs.count()
                number_of_consumption_records_next_cycle = current_qs.count()
                current_consumption = current_qs.aggregate(sum=Sum(Coalesce(F(ART_CONSUMPTION), 0) + Coalesce(F(PMTCT_CONSUMPTION), 0))).get(SUM, 0)
                prev_consumption = prev_qs.aggregate(sum=Sum(Coalesce(F(ART_CONSUMPTION), 0) + Coalesce(F(PMTCT_CONSUMPTION), 0))).get(SUM, 0)
                include_record = current_consumption >= threshold
                if include_record:
                    if number_of_consumption_records == 0 or number_of_consumption_records_next_cycle == 0 or record.reporting_status == False:
                        not_reporting += 1
                    elif prev_consumption != 0 and (0.5 <= (current_consumption / prev_consumption) <= 1.5 or 0.5 <= (prev_consumption / current_consumption) <= 1.5):
                        yes += 1
                        result = YES
                    else:
                        no += 1
                        result = NO
                    self.record_result_for_facility(record, result, formulation[NAME])
            self.build_cycle_formulation_score(cycle, formulation[NAME], yes, no, not_reporting, total_count)
