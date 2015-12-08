from django.db.models import Sum, F

from dashboard.checks.common import Check
from dashboard.helpers import CONSUMPTION_AND_PATIENTS
from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, FacilityCycleRecord, FacilityConsumptionRecord, CycleFormulationTestScore


class ConsumptionAndPatients(Check):
    def run(self, cycle):
        formulations = [
            {"name": "TDF/3TC/EFV (Adult)", "patient_query": "TDF/3TC/EFV", "consumption_query": "Efavirenz (TDF/3TC/EFV)", "model": AdultPatientsRecord, "ratio": 2.0},
            {"name": "ABC/3TC (Paed)", "patient_query": "ABC/3TC", "consumption_query": "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]", "model": PAEDPatientsRecord, "ratio": 4.6},
            {"name": "EFV200 (Paed)", "patient_query": "EFV", "consumption_query": "(EFV) 200mg [Pack 90]", "model": PAEDPatientsRecord, "ratio": 1}
        ]
        for formulation in formulations:
            yes = 0
            no = 0
            not_reporting = 0
            qs = FacilityCycleRecord.objects.filter(cycle=cycle)
            total_count = qs.count()
            for record in qs:
                try:
                    consumption_qs = FacilityConsumptionRecord.objects.filter(facility_cycle=record, formulation__icontains=formulation["consumption_query"])
                    patient_qs = formulation['model'].objects.filter(facility_cycle=record, formulation__icontains=formulation["patient_query"])
                    number_of_consumption_records = consumption_qs.count()
                    number_of_patient_records = patient_qs.count()
                    patient_sum = patient_qs.aggregate(sum=Sum(F('existing') + F('new'))).get('sum', 0)
                    art_consumption = consumption_qs.aggregate(sum=Sum('art_consumption')).get('sum', 0)
                    total = patient_sum + art_consumption
                    adjusted_consumption_sum = art_consumption / formulation["ratio"]
                    if number_of_consumption_records == 0 or number_of_patient_records == 0:
                        not_reporting += 1
                    elif total == 0 or 0.7 * patient_sum < adjusted_consumption_sum < 1.429 * patient_sum:
                        yes += 1
                    else:
                        no += 1
                except TypeError as e:
                    no += 1

            score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=CONSUMPTION_AND_PATIENTS, formulation=formulation['consumption_query'])
            yes_rate = float(yes * 100) / float(total_count)
            no_rate = float(no * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = no_rate
            score.not_reporting = not_reporting_rate
            score.save()
