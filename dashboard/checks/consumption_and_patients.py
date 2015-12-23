from django.db.models import Sum, F
from django.db.models.functions import Coalesce

from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import CONSUMPTION_AND_PATIENTS, YES, NO, NOT_REPORTING, F3, F2, F1
from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, Cycle, Consumption

NAME = "name"

MODEL = 'model'

RATIO = "ratio"

ART_CONSUMPTION = 'art_consumption'

PATIENT_QUERY = "patient_query"

CONSUMPTION_QUERY = "consumption_query"

SUM = 'sum'

NEW = 'new'

EXISTING = 'existing'

F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
F3_QUERY = "(EFV) 200mg [Pack 90]"
F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"


class ConsumptionAndPatients(CycleFormulationCheck):
    test = CONSUMPTION_AND_PATIENTS
    formulations = [{NAME: F1, PATIENT_QUERY: "TDF/3TC/EFV", CONSUMPTION_QUERY: F1_QUERY, MODEL: AdultPatientsRecord, RATIO: 2.0}, {NAME: F2, PATIENT_QUERY: "ABC/3TC", CONSUMPTION_QUERY: F2_QUERY, MODEL: PAEDPatientsRecord, RATIO: 4.6}, {NAME: F3, PATIENT_QUERY: "EFV", CONSUMPTION_QUERY: F3_QUERY, MODEL: PAEDPatientsRecord, RATIO: 1}]

    def run(self, cycle):

        formulations = self.formulations
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                try:
                    result = NOT_REPORTING
                    consumption_qs = Consumption.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY])
                    patient_qs = formulation[MODEL].objects.filter(facility_cycle=record, formulation__icontains=formulation[PATIENT_QUERY])
                    number_of_consumption_records = consumption_qs.count()
                    number_of_patient_records = patient_qs.count()
                    patient_sum = patient_qs.aggregate(sum=Sum(Coalesce(F(EXISTING) + F(NEW), 0))).get(SUM, 0)
                    art_consumption = consumption_qs.aggregate(sum=Sum(Coalesce(ART_CONSUMPTION, 0))).get(SUM, 0)
                    total = patient_sum + art_consumption
                    adjusted_consumption_sum = art_consumption / formulation[RATIO]
                except TypeError as e:
                    not_reporting += 1
                    adjusted_consumption_sum = total = 0
                finally:
                    no, not_reporting, result, yes = self.calculate_score(adjusted_consumption_sum, patient_sum, number_of_consumption_records, number_of_patient_records, total, yes, no, not_reporting, result)
                self.record_result_for_facility(record, result, formulation[NAME])
            self.build_cycle_formulation_score(cycle, formulation[NAME], yes, no, not_reporting, total_count)

    def calculate_score(self, adjusted_consumption_sum, patient_sum, number_of_consumption_records, number_of_patient_records, total, yes, no, not_reporting, result):
        if number_of_consumption_records == 0 or number_of_patient_records == 0:
            not_reporting += 1
        elif total == 0 or (0.7 * patient_sum) < adjusted_consumption_sum < (1.429 * patient_sum):
            yes += 1
            result = YES
        else:
            no += 1
            result = NO
        return no, not_reporting, result, yes
