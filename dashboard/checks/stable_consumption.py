from django.db.models import Sum, F

from dashboard.checks.common import Check
from dashboard.checks.different_orders_over_time import get_next_cycle
from dashboard.helpers import STABLE_CONSUMPTION
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord, CycleFormulationTestScore

SUM = 'sum'

THRESHOLD = "threshold"

CONSUMPTION_QUERY = "consumption_query"

PMTCT_CONSUMPTION = 'pmtct_consumption'

ART_CONSUMPTION = 'art_consumption'


class StableConsumption(Check):
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
                    if number_of_consumption_records == 0 or number_of_consumption_records_next_cycle == 0:
                        not_reporting += 1
                    elif 0.5 < (next_cycle_consumption / current_cycle_consumption) < 1.5:
                        yes += 1
                    else:
                        no += 1
                except TypeError as e:
                    no += 1

            score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=STABLE_CONSUMPTION, formulation=formulation[CONSUMPTION_QUERY])
            yes_rate = float(yes * 100) / float(total_count)
            no_rate = float(no * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = no_rate
            score.not_reporting = not_reporting_rate
            score.save()
