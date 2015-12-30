import operator

from django.db.models import Sum, F
from django.db.models.functions import Coalesce

from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import CONSUMPTION_AND_PATIENTS, YES, NO, NOT_REPORTING, F3, F2, F1
from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, Cycle, Consumption

FIELDS = "fields"

PMTCT_CONSUMPTION = "pmtct_consumption"

NAME = "name"

MODEL = 'model'

RATIO = "ratio"

ART_CONSUMPTION = 'art_consumption'

PATIENT_QUERY = "patient_query"

CONSUMPTION_QUERY = "consumption_query"

SUM = 'sum'

NEW = 'new'

EXISTING = 'existing'

F1_QUERY = "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"
F3_QUERY = "Efavirenz (EFV) 200mg [Pack 90]"
F2_QUERY = "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"


class ConsumptionAndPatients(CycleFormulationCheck):
    test = CONSUMPTION_AND_PATIENTS
    formulations = [{NAME: F1, PATIENT_QUERY: "TDF/3TC/EFV", CONSUMPTION_QUERY: F1_QUERY, MODEL: AdultPatientsRecord, RATIO: 2.0, FIELDS: [Coalesce(F(ART_CONSUMPTION), 0), Coalesce(F(PMTCT_CONSUMPTION), 0)]},
                    {NAME: F2, PATIENT_QUERY: "ABC/3TC", CONSUMPTION_QUERY: F2_QUERY, MODEL: PAEDPatientsRecord, RATIO: 4.6, FIELDS: [Coalesce(F(ART_CONSUMPTION), 0)]},
                    {NAME: F3, PATIENT_QUERY: "EFV", CONSUMPTION_QUERY: F3_QUERY, MODEL: PAEDPatientsRecord, RATIO: 1, FIELDS: [Coalesce(F(ART_CONSUMPTION), 0)]}]

    def run(self, cycle):

        formulations = self.formulations
        for formulation in formulations:
            yes = 0
            no = 0
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle, reporting_status=True)
            total_count = qs.count()
            not_reporting = Cycle.objects.filter(cycle=cycle, reporting_status=False).count()
            for record in qs:
                result = NOT_REPORTING
                consumption_qs = Consumption.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(facility_cycle=record, formulation__icontains=formulation[CONSUMPTION_QUERY])
                patient_qs = formulation[MODEL].objects.filter(facility_cycle=record, formulation__icontains=formulation[PATIENT_QUERY])
                number_of_consumption_records = consumption_qs.count()
                number_of_patient_records = patient_qs.count()
                consumption_field = reduce(operator.add, formulation[FIELDS])
                patient_sum = patient_qs.aggregate(sum=Sum(Coalesce(F(EXISTING), 0) + Coalesce(F(NEW), 0))).get(SUM, 0)
                art_consumption = consumption_qs.aggregate(sum=Coalesce(Sum(consumption_field), 0)).get(SUM, 0)
                if patient_sum is None:
                    patient_sum = 0
                if art_consumption is None:
                    art_consumption = 0
                total = patient_sum + art_consumption
                adjusted_consumption_sum = art_consumption / formulation[RATIO]
                no, not_reporting, result, yes = self.calculate_score(adjusted_consumption_sum, patient_sum, number_of_consumption_records, number_of_patient_records, total, yes, no, not_reporting, result)
                self.record_result_for_facility(record, result, formulation[NAME])
            self.build_cycle_formulation_score(cycle, formulation[NAME], yes, no, not_reporting, total_count)

    def calculate_score(self, adjusted_consumption_sum, patient_sum, number_of_consumption_records, number_of_patient_records, total, yes, no, not_reporting, result):
        numerator = adjusted_consumption_sum
        denominator = patient_sum
        if patient_sum > adjusted_consumption_sum:
            numerator = patient_sum
            denominator = adjusted_consumption_sum
        if number_of_consumption_records == 0 or number_of_patient_records == 0:
            not_reporting += 1
        elif total == 0 or (denominator != 0 and 0.7 < abs(numerator / denominator) < 1.429):
            yes += 1
            result = YES
        else:
            no += 1
            result = NO
        return no, not_reporting, result, yes
