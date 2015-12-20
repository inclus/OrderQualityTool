import operator

from django.db.models import Q, F, Sum

from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import GUIDELINE_ADHERENCE, NOT_REPORTING, YES, NO
from dashboard.models import Cycle, Consumption

FIELDS = "fields"

NAME = "name"

MODEL = 'model'

RATIO = "ratio"

ART_CONSUMPTION = 'art_consumption'

DF2 = "data_field_2"

DF1 = "data_field_1"

SUM = 'sum'

NEW = 'new'

EXISTING = 'existing'


class GuideLineAdherence(CycleFormulationCheck):
    test = GUIDELINE_ADHERENCE

    def run(self, cycle):
        formulations = [
            {NAME: "Adult 1L", DF2: ["(AZT/3TC) 300mg/150mg [Pack 60]", "(AZT/3TC/NVP) 300mg/150mg/200mg [Pack 60]"], DF1: ["TDF/3TC"], RATIO: 80.0, FIELDS: ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"]},
            {NAME: "Adult 2L", DF2: ["(LPV/r) 200mg/50mg [Pack 120]"], DF1: ["(ATV/r) 300mg/100mg [Pack 30]"], RATIO: 73.3, FIELDS: ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"]},
            {NAME: "Paed 1L", DF2: ["(AZT/3TC/NVP) 60mg/30mg/50mg [Pack 60]", "(AZT/3TC) 60mg/30mg [Pack 60]"], DF1: ["(ABC/3TC) 60mg/30mg [Pack 60]"], RATIO: 80.0, FIELDS: ["estimated_number_of_new_patients"]}
        ]

        for formulation in formulations:
            name = formulation[NAME]
            qs = Cycle.objects.filter(cycle=cycle)
            total_count = qs.count()
            not_reporting = 0
            yes = 0
            no = 0
            ratio = formulation[RATIO] / 100.0
            for record in qs:
                try:
                    df1_filter = reduce(operator.or_, (Q(formulation__contains=item) for item in formulation[DF1]))
                    df1_sum_fields = reduce(operator.add, (F(item) for item in formulation[FIELDS]))
                    df2_filter = reduce(operator.or_, (Q(formulation__contains=item) for item in formulation[DF1]))
                    df1_qs = Consumption.objects.filter(facility_cycle=record).filter(df1_filter)
                    df2_qs = Consumption.objects.filter(facility_cycle=record).filter(df2_filter)
                    df1_count = df1_qs.count()
                    df2_count = df2_qs.count()
                    sum_df1 = df1_qs.aggregate(sum=Sum(df1_sum_fields)).get("sum", 0)
                    sum_df2 = df2_qs.aggregate(sum=Sum(df1_sum_fields)).get("sum", 0)
                    total = sum_df1 + sum_df2
                    result = NOT_REPORTING
                    if df1_count == 0 or df2_count == 0:
                        not_reporting += 1
                    elif total == 0 or sum_df1 < (ratio * total):
                        yes += 1
                        result = YES
                    else:
                        no += 1
                        result = NO

                except TypeError as e:
                    no += 1
                    result = NO
                finally:
                    test_name = "%s%s" % (GUIDELINE_ADHERENCE, name.replace(" ", ""))
                    self.record_result_for_facility(record, result, test=test_name)
            self.build_cycle_formulation_score(cycle, name, yes, no, not_reporting, total_count)
