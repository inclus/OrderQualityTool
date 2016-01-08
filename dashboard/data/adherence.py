import pydash

from dashboard.data.utils import QCheck, NAME, FORMULATION, values_for_records
from dashboard.helpers import NOT_REPORTING, YES, NO

ADULT_2L = "Adult 2L"

PAED_1L = "Paed 1L"

ADULT_1L = "Adult 1L"

FIELDS = "fields"

MODEL = 'model'

RATIO = "ratio"

ART_CONSUMPTION = 'art_consumption'

DF2 = "data_field_2"

DF1 = "data_field_1"

SUM = 'sum'

NEW = 'new'

EXISTING = 'existing'


class GuidelineAdherenceCheckAdult1L(QCheck):
    test = "guidelineAdherenceAdult1L"
    combinations = [{
        NAME: 'DEFAULT',
        DF2: ["Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]",
              "Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 300mg/150mg/200mg [Pack 60]"],
        DF1: ["Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]",
              "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"],
        RATIO: 0.80,
        FIELDS: ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"]
    }]

    def filter_records(self, facility_name, formulation_names):
        records = self.report.cs[facility_name]

        def filter_func(x):
            for f in formulation_names:
                if f in x[FORMULATION]:
                    return True
            return False

        return pydash.select(records, filter_func)

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        facility_name = facility[NAME]
        ratio = combination[RATIO]
        df1_records = self.filter_records(facility_name, combination[DF1])
        df2_records = self.filter_records(facility_name, combination[DF2])
        df1_count = len(df1_records)
        df2_count = len(df2_records)
        df1_values = values_for_records(combination[FIELDS], df1_records)
        df2_values = values_for_records(combination[FIELDS], df2_records)
        sum_df1 = pydash.chain(df1_values).reject(lambda x: x is None).sum().value()
        sum_df2 = pydash.chain(df2_values).reject(lambda x: x is None).sum().value()
        all_df1_fields_are_blank = pydash.every(df1_values, lambda x: x is None)
        all_df2_fields_are_blank = pydash.every(df2_values, lambda x: x is None)
        return calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, yes, no,
                               not_reporting, all_df1_fields_are_blank,
                               all_df2_fields_are_blank)


class GuidelineAdherenceCheckAdult2L(GuidelineAdherenceCheckAdult1L):
    test = "guidelineAdherenceAdult2L"
    combinations = [{
        NAME: 'DEFAULT',
        DF2: ["Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"],
        DF1: ["Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"],
        RATIO: 0.73,
        FIELDS: ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"]
    }]


class GuidelineAdherenceCheckPaed1L(GuidelineAdherenceCheckAdult1L):
    test = "guidelineAdherencePaed1L"
    combinations = [{
        NAME: 'DEFAULT',
        DF2: ["Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 60mg/30mg/50mg [Pack 60]",
              "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"],
        DF1: ["Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"],
        RATIO: 0.80,
        FIELDS: ["estimated_number_of_new_patients"]
    }]


def calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, yes, no, not_reporting,
                    all_df1_fields_are_blank=False, all_df2_fields_are_blank=False):
    total = sum_df1 + sum_df2
    has_blanks = (all_df2_fields_are_blank or all_df1_fields_are_blank)
    has_no_blanks = not has_blanks
    has_no_records = df1_count == 0 or df2_count == 0
    adjusted_total = (ratio * total)
    df1_is_at_least_adjusted_total = sum_df1 >= adjusted_total
    result = NOT_REPORTING
    if has_no_records:
        not_reporting += 1
    elif has_no_blanks and ((sum_df1 == 0 and sum_df2 == 0) or df1_is_at_least_adjusted_total):
        yes += 1
        result = YES
    else:
        no += 1
        result = NO
    return result, no, not_reporting, yes