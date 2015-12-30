import operator

from django.db.models import Q, F, Sum
from django.db.models.functions import Coalesce

from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import GUIDELINE_ADHERENCE, NOT_REPORTING, YES, NO
from dashboard.models import Cycle, Consumption

ADULT_2L = "Adult 2L"

PAED_1L = "Paed 1L"

ADULT_1L = "Adult 1L"

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


class GuidelineAdherence(CycleFormulationCheck):
    test = GUIDELINE_ADHERENCE
    formulations = [
        {
            NAME: ADULT_1L,
            DF2: ["Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]", "Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 300mg/150mg/200mg [Pack 60]"],
            DF1: ["Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]", "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"],
            RATIO: 80.0,
            FIELDS: ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"]},
        {
            NAME: ADULT_2L, DF2: ["Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"],
            DF1: ["Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"],
            RATIO: 73.3,
            FIELDS: ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"]
        },
        {
            NAME: PAED_1L,
            DF2: ["Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 60mg/30mg/50mg [Pack 60]", "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"],
            DF1: ["Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"],
            RATIO: 80.0,
            FIELDS: ["estimated_number_of_new_patients"]
        }
    ]

    def run(self, cycle):
        formulations = self.formulations

        for formulation in formulations:
            name = formulation[NAME]
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip', 'facility__warehouse').filter(cycle=cycle, reporting_status=True)
            total_count = Cycle.objects.filter(cycle=cycle).count()
            not_reporting = Cycle.objects.filter(cycle=cycle, reporting_status=False).count()
            yes = 0
            no = 0
            ratio = formulation[RATIO] / 100.0
            for record in qs:
                df1_filter = reduce(operator.or_, (Q(formulation__icontains=item) for item in formulation[DF1]))
                df1_sum_fields = reduce(operator.add, (Coalesce(F(item), 0) for item in formulation[FIELDS]))
                df2_filter = reduce(operator.or_, (Q(formulation__icontains=item) for item in formulation[DF2]))
                df1_qs = Consumption.objects.filter(facility_cycle=record).filter(df1_filter)
                df2_qs = Consumption.objects.filter(facility_cycle=record).filter(df2_filter)
                df1_count = df1_qs.count()
                df2_count = df2_qs.count()
                sum_df1 = self.get_sum(df1_qs, df1_sum_fields)
                all_df1_fields_are_blank = self.check_if_all_fields_null(df1_qs, formulation)
                all_df2_fields_are_blank = self.check_if_all_fields_null(df2_qs, formulation)
                sum_df2 = self.get_sum(df2_qs, df1_sum_fields)
                no, not_reporting, result, yes = self.calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, yes, no, not_reporting, all_df1_fields_are_blank, all_df2_fields_are_blank)
                test_name = "%s%s" % (GUIDELINE_ADHERENCE, name.replace(" ", ""))
                self.record_result_for_facility(record, result, test=test_name)
            self.build_cycle_formulation_score(cycle, name, yes, no, not_reporting, total_count)

    def get_sum(self, queryset, fields_to_sum):
        aggregate_result = queryset.aggregate(sum=Coalesce(Sum(fields_to_sum), 0))
        return aggregate_result.get("sum", 0)

    def calculate_score(self, df1_count, df2_count, sum_df1, sum_df2, ratio, yes, no, not_reporting, all_df1_fields_are_blank=False, all_df2_fields_are_blank=False):
        total = sum_df1 + sum_df2
        result = NOT_REPORTING
        has_blanks = (all_df2_fields_are_blank or all_df1_fields_are_blank)
        has_no_blanks = not has_blanks
        has_no_records = df1_count == 0 or df2_count == 0
        adjusted_total = (ratio * total)
        df1_is_at_least_adjusted_total = sum_df1 >= adjusted_total
        df1_is_less_than_adjusted_total = sum_df1 < adjusted_total
        if has_no_records:
            not_reporting += 1
        elif has_no_blanks and (total == 0 or df1_is_at_least_adjusted_total):
            yes += 1
            result = YES
        elif df1_is_less_than_adjusted_total or has_blanks:
            no += 1
            result = NO
        else:
            pass
        return no, not_reporting, result, yes

    def check_if_all_fields_null(self, qs, formulation):
        filter = dict((item + "__isnull", True) for item in formulation[FIELDS])
        return qs.filter(**filter).exists()
