import operator
from django.db.models import Q, F, Sum
from django.db.models.functions import Coalesce
from dashboard.checks.common import Check
from dashboard.helpers import NNRTI_CURRENT_ADULTS, NNRTI_CURRENT_PAED, NNRTI_NEW_ADULTS, NNRTI_NEW_PAED, NOT_REPORTING, \
    YES, NO
from dashboard.models import Cycle, CycleScore, Consumption

TEST = "test"

FIELDS = "fields"

RATIO = "ratio"

DF2 = "data_field_2"

DF1 = "data_field_1"

EXISTING = 'existing'


class NNRTI(Check):
    formulations = [
        {
            TEST: NNRTI_CURRENT_ADULTS,
            DF2: [
                "Efavirenz (EFV) 600mg [Pack 30]",
                "Nevirapine (NVP) 200mg [Pack 60]",
                "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]",
                "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"
            ],
            DF1: [
                "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]",
                "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]",
                "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
            ],
            RATIO: 1,
            FIELDS: [
                "pmtct_consumption",
                "art_consumption"
            ]},
        {
            TEST: NNRTI_CURRENT_PAED,
            DF2: [
                "Efavirenz (EFV) 200mg [Pack 90]",
                "Nevirapine (NVP) 50mg [Pack 60]",
                "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
                "Lopinavir/Ritonavir (LPV/r) 100mg/25mg",
            ],
            DF1: [
                "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]",
                "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
            ],
            RATIO: 4.6,
            FIELDS: [
                "art_consumption"
            ]},
        {
            TEST: NNRTI_NEW_ADULTS,
            DF2: [
                "Efavirenz (EFV) 600mg [Pack 30]",
                "Nevirapine (NVP) 200mg [Pack 60]",
                "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]",
                "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"
            ],
            DF1: [
                "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]",
                "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]",
                "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
            ],
            RATIO: 1,
            FIELDS: [
                "estimated_number_of_new_patients",
                "estimated_number_of_new_pregnant_women"
            ]},
        {
            TEST: NNRTI_NEW_PAED,
            DF2: [
                "Efavirenz (EFV) 200mg [Pack 90]",
                "Nevirapine (NVP) 50mg [Pack 60]",
                "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
                "Lopinavir/Ritonavir (LPV/r) 100mg/25mg"],
            DF1: [
                "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]",
                "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
            ],
            RATIO: 1,
            FIELDS: [
                "estimated_number_of_new_patients",
                "estimated_number_of_new_pregnant_women"
            ]},
    ]

    def run(self, cycle):
        for formulation in self.formulations:
            test = formulation[TEST]
            qs = Cycle.objects.select_related('facility', 'facility__district', 'facility__ip',
                                              'facility__warehouse').filter(cycle=cycle, reporting_status=True)
            total_count = Cycle.objects.filter(cycle=cycle).count()
            not_reporting = Cycle.objects.filter(cycle=cycle, reporting_status=False).count()
            yes = 0
            no = 0
            for record in qs:
                no, not_reporting, yes = self.process_facility(record, formulation, yes, no, not_reporting)
            score, _ = CycleScore.objects.get_or_create(cycle=cycle, test=test)
            yes_rate = float(yes * 100) / float(total_count)
            not_reporting_rate = float(not_reporting * 100) / float(total_count)
            score.yes = yes_rate
            score.no = float(no * 100) / float(total_count)
            score.not_reporting = not_reporting_rate
            score.save()

    def process_facility(self, record, formulation, yes, no, not_reporting):
        ratio = formulation[RATIO]
        test = formulation[TEST]
        df1_filter = reduce(operator.or_, (Q(formulation__icontains=item) for item in formulation[DF1]))
        sum_fields = reduce(operator.add, (Coalesce(F(item), 0) for item in formulation[FIELDS]))
        df2_filter = reduce(operator.or_, (Q(formulation__icontains=item) for item in formulation[DF2]))
        df1_qs = Consumption.objects.filter(facility_cycle=record).filter(df1_filter)
        df2_qs = Consumption.objects.filter(facility_cycle=record).filter(df2_filter)
        df1_count = df1_qs.count()
        df2_count = df2_qs.count()
        df1_agg = df1_qs.aggregate(sum=Coalesce(Sum(sum_fields), 0))
        df2_agg = df2_qs.aggregate(sum=Coalesce(Sum(sum_fields), 0))
        sum_df1 = df1_agg.get("sum", 0)
        sum_df2 = df2_agg.get("sum", 0)
        total = sum_df1 + sum_df2
        no, not_reporting, result, yes = self.compare_values(ratio, no, not_reporting, yes, df1_count, df2_count,
                                                             sum_df1, sum_df2, total)
        self.record_result_for_facility(record, result, test=test)
        return no, not_reporting, yes

    def compare_values(self, ratio, no, not_reporting, yes, df1_count, df2_count, sum_df1, sum_df2, total):
        adjusted_sum_df1 = (sum_df1 / ratio)
        numerator = adjusted_sum_df1
        denominator = sum_df2
        result = None
        if abs(adjusted_sum_df1) > abs(sum_df2):
            numerator = sum_df2
            denominator = adjusted_sum_df1

        if df1_count == 0 or df2_count == 0:
            not_reporting += 1
            result = NOT_REPORTING
        elif total == 0 or (denominator != 0 and 0.7 <= abs(numerator / denominator) <= 1.429):
            yes += 1
            result = YES
        elif denominator != 0 and (abs(numerator / denominator) < 0.7 or abs(numerator / denominator) > 1.429):
            no += 1
            result = NO
        else:
            pass

        return no, not_reporting, result, yes
