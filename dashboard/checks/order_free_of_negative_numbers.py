import operator

from dashboard.checks.common import Check
from dashboard.helpers import ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS
from dashboard.models import FacilityConsumptionRecord, FacilityCycleRecord, CycleFormulationTestScore


class OrderFormFreeOfNegativeNumbers(Check):
    def run(self, cycle):
        values = FacilityConsumptionRecord.objects.filter(facility_cycle__cycle=cycle).order_by().values('formulation').distinct()
        for formulation in values:
            name = formulation["formulation"]
            filter_list = [Q(opening_balance__lt=0), Q(quantity_received__lt=0), Q(pmtct_consumption__lt=0), Q(art_consumption__lt=0), Q(estimated_number_of_new_pregnant_women__lt=0), Q(total_quantity_to_be_ordered__lt=0)]
            total_count = FacilityCycleRecord.objects.filter(cycle=cycle).count()
            not_reporting = FacilityCycleRecord.objects.filter(cycle=cycle, reporting_status=False).count()
            valid = FacilityConsumptionRecord.objects.filter(facility_cycle__cycle=cycle, formulation=name).exclude(reduce(operator.or_, filter_list)).count()
            score, _ = CycleFormulationTestScore.objects.get_or_create(cycle=cycle, test=ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, formulation=name)
            yes_rate = float(valid * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = 100 - yes_rate - not_reporting_rate
            score.not_reporting = not_reporting_rate
            score.save()
