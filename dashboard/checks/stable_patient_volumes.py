from django.db.models import Sum, F
from django.db.models.functions import Coalesce

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
    F1_QUERY = "TDF/3TC/EFV"
    F2_QUERY = "ABC/3TC"
    F3_QUERY = "EFV"

    def run(self, cycle):
        prev_cycle = get_prev_cycle(cycle)
        formulations = [
            {PATIENT_QUERY: self.F1_QUERY, NAME: F1, MODEL: AdultPatientsRecord, THRESHOLD: 10},
            {PATIENT_QUERY: self.F2_QUERY, NAME: F2, MODEL: PAEDPatientsRecord, THRESHOLD: 5},
            {PATIENT_QUERY: self.F3_QUERY, NAME: F3, MODEL: PAEDPatientsRecord, THRESHOLD: 5}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            threshold = formulation[THRESHOLD]
            model_class = formulation[MODEL]
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle, reporting_status=True)
            not_reporting = total_count = Cycle.objects.filter(cycle=cycle, reporting_status=False).count()
            for record in qs:
                current_qs = model_class.objects.filter(facility_cycle=record, formulation__icontains=formulation[PATIENT_QUERY])
                prev_qs = model_class.objects.filter(facility_cycle__facility=record.facility, facility_cycle__cycle=prev_cycle, formulation__icontains=formulation[PATIENT_QUERY])
                result = NOT_REPORTING
                number_of_prev_patient_records = prev_qs.count()
                number_of_current_patient_records = current_qs.count()
                current_population = current_qs.aggregate(sum=Sum(Coalesce(F(EXISTING), 0) + Coalesce(F(NEW), 0))).get(SUM, 0)
                prev_population = prev_qs.aggregate(sum=Sum(Coalesce(F(EXISTING), 0) + Coalesce(F(NEW), 0))).get(SUM, 0)
                if current_population >= threshold:
                    total_count += 1
                    if number_of_prev_patient_records == 0 or number_of_current_patient_records == 0 or prev_population < 1:
                        not_reporting += 1
                    elif 0.5 <= (current_population / prev_population) <= 1.5:
                        yes += 1
                        result = YES
                    else:
                        no += 1
                        result = NO
                    self.record_result_for_facility(record, result, formulation[NAME])

            self.build_cycle_formulation_score(cycle, formulation[NAME], yes, no, not_reporting, total_count)
