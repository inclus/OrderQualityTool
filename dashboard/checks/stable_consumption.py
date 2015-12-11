from django.db.models import Sum, F

from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_next_cycle
from dashboard.helpers import STABLE_CONSUMPTION, NOT_REPORTING, NO, YES
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord

SUM = 'sum'

THRESHOLD = "threshold"

CONSUMPTION_QUERY = "consumption_query"

PMTCT_CONSUMPTION = 'pmtct_consumption'

ART_CONSUMPTION = 'art_consumption'


class StableConsumption(CycleFormulationCheck):
    test = STABLE_CONSUMPTION

    def run(self, cycle):
        next_cycle = get_next_cycle(cycle)
        formulations = [
            {"name": "TDF/3TC/EFV (Adult)", CONSUMPTION_QUERY: "Efavirenz (TDF/3TC/EFV)", THRESHOLD: 20},
            {"name": "ABC/3TC (Paed)", CONSUMPTION_QUERY: "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]", THRESHOLD: 10},
            {"name": "EFV200 (Paed)", CONSUMPTION_QUERY: "(EFV) 200mg [Pack 90]", THRESHOLD: 10}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            threshold = formulation[THRESHOLD]
            qs = FacilityCycleRecord.objects.filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                try:
                    current_cycle_qs = FacilityConsumptionRecord.objects.annotate(consumption=Sum(F(ART_CONSUMPTION) + F(PMTCT_CONSUMPTION))).filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY], consumption__gte=threshold)
                    next_cycle_qs = FacilityConsumptionRecord.objects.annotate(consumption=Sum(F(ART_CONSUMPTION) + F(PMTCT_CONSUMPTION))).filter(facility_cycle__facility=record.facility, facility_cycle__cycle=next_cycle, formulation__icontains=formulation[CONSUMPTION_QUERY], consumption__gte=threshold)
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
                    self.record_result_for_facility(record, result, formulation[CONSUMPTION_QUERY])
            self.build_cycle_formulation_score(cycle, formulation[CONSUMPTION_QUERY], yes, no, not_reporting, total_count)
