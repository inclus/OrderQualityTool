from django.db.models import Sum, F

from dashboard.checks.common import CycleFormulationCheck
from dashboard.checks.different_orders_over_time import get_prev_cycle
from dashboard.helpers import STABLE_PATIENT_VOLUMES, NO, YES, NOT_REPORTING, F3, F2, F1
from dashboard.models import Cycle, AdultPatientsRecord, PAEDPatientsRecord

NAME = "name"

NEW = "new"

EXISTING = "existing"

SUM = 'sum'

THRESHOLD = "threshold"

CONSUMPTION_QUERY = "consumption_query"

PMTCT_CONSUMPTION = 'pmtct_consumption'

ART_CONSUMPTION = 'art_consumption'

MODEL = 'model'

PATIENT_QUERY = 'patients_query'


class StablePatientVolumes(CycleFormulationCheck):
    test = STABLE_PATIENT_VOLUMES

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {PATIENT_QUERY: "TDF/3TC/EFV", NAME: F1, CONSUMPTION_QUERY: "Efavirenz (TDF/3TC/EFV)", MODEL: AdultPatientsRecord, THRESHOLD: 10},
            {PATIENT_QUERY: "ABC/3TC", NAME: F2, CONSUMPTION_QUERY: "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]", MODEL: PAEDPatientsRecord, THRESHOLD: 5},
            {PATIENT_QUERY: "EFV", NAME: F3, CONSUMPTION_QUERY: "(EFV) 200mg [Pack 90]", MODEL: PAEDPatientsRecord, THRESHOLD: 5}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            threshold = formulation[THRESHOLD]
            model_class = formulation[MODEL]
            qs = Cycle.objects.filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                try:
                    next_cycle_qs = model_class.objects.annotate(population=Sum(F(EXISTING) + F(NEW))).filter(facility_cycle=record, formulation__icontains=formulation[PATIENT_QUERY], population__gte=threshold)
                    current_cycle_qs = model_class.objects.annotate(population=Sum(F(EXISTING) + F(NEW))).filter(facility_cycle__facility=record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=formulation[PATIENT_QUERY], population__gte=threshold)
                    number_of_patient_records = current_cycle_qs.count()
                    number_of_patient_records_next_cycle = next_cycle_qs.count()
                    next_cycle_population = next_cycle_qs.aggregate(sum=Sum(F(EXISTING) + F(NEW))).get(SUM, 0)
                    current_cycle_population = current_cycle_qs.aggregate(sum=Sum(F(EXISTING) + F(NEW))).get(SUM, 0)
                    result = NOT_REPORTING
                    if number_of_patient_records == 0 or number_of_patient_records_next_cycle == 0:
                        not_reporting += 1
                    elif 0.5 < (next_cycle_population / current_cycle_population) < 1.5:
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
