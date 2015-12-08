import operator

from django.db.models import Q

from dashboard.checks.common import Check
from dashboard.helpers import ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS
from dashboard.models import FacilityConsumptionRecord, FacilityCycleRecord, CycleFormulationTestScore


class OrderFormFreeOfNegativeNumbers(Check):
    def run(self, cycle):
        formulations = [
            {"name": "TDF/3TC/EFV (Adult)", "consumption_query": "Efavirenz (TDF/3TC/EFV)"},
            {"name": "ABC/3TC (Paed)", "consumption_query": "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
            {"name": "EFV200 (Paed)", "consumption_query": "EFV) 200mg [Pack 90]"}
        ]
        for formulation in formulations:
            name = formulation["consumption_query"]
            filter_list = [Q(opening_balance__lt=0), Q(quantity_received__lt=0), Q(pmtct_consumption__lt=0), Q(art_consumption__lt=0), Q(estimated_number_of_new_pregnant_women__lt=0), Q(total_quantity_to_be_ordered__lt=0)]
            total_count = FacilityCycleRecord.objects.filter(cycle=cycle).count()
            not_reporting = FacilityCycleRecord.objects.filter(cycle=cycle, reporting_status=False).count()
            valid = FacilityConsumptionRecord.objects.filter(facility_cycle__cycle=cycle, formulation__icontains=name).exclude(reduce(operator.or_, filter_list)).count()
            score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, formulation=name)
            yes_rate = float(valid * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = 100 - yes_rate - not_reporting_rate
            score.not_reporting = not_reporting_rate
            score.save()
