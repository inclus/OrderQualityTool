import pydash

from dashboard.data.utils import QCheck, NAME, RATIO, FIELDS, FORMULATION, values_for_records
from dashboard.helpers import NNRTI_CURRENT_ADULTS, NNRTI_CURRENT_PAED, NNRTI_NEW_PAED, NNRTI_NEW_ADULTS, NOT_REPORTING, \
    YES, NO

DF2 = "data_field_2"

DF1 = "data_field_1"


class NNRTICURRENTADULTSCheck(QCheck):
    test = NNRTI_CURRENT_ADULTS
    combinations = [{
        NAME: 'DEFAULT',
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
        FIELDS: [
            "pmtct_consumption",
            "art_consumption"
        ]
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
        df1_records = self.filter_records(facility_name, combination[DF1])
        df2_records = self.filter_records(facility_name, combination[DF2])
        df1_count = len(df1_records)
        df2_count = len(df2_records)
        df1_values = values_for_records(combination[FIELDS], df1_records)
        df2_values = values_for_records(combination[FIELDS], df2_records)
        sum_df1 = pydash.chain(df1_values).reject(lambda x: x is None).sum().value()
        sum_df2 = pydash.chain(df2_values).reject(lambda x: x is None).sum().value()
        total = sum_df2 + sum_df1
        numerator = sum_df1
        denominator = sum_df2
        result = None
        if abs(sum_df1) > abs(sum_df2):
            numerator = sum_df2
            denominator = sum_df1

        if df1_count == 0 or df2_count == 0:
            not_reporting += 1
            result = NOT_REPORTING
        elif total == 0 or (denominator != 0 and 0.7 <= abs(numerator / denominator) <= 1.429):
            yes += 1
            result = YES
        elif denominator != 0 and (abs(numerator / denominator) < 1.0 or abs(numerator / denominator) > 1.429):
            no += 1
            result = NO
        else:
            pass

        return result, no, not_reporting, yes


class NNRTICURRENTPAEDCheck(NNRTICURRENTADULTSCheck):
    test = NNRTI_CURRENT_PAED
    combinations = [{
        NAME: 'DEFAULT',

        DF2: [
            "Nevirapine (NVP) 50mg [Pack 60]",
            "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
            "Lopinavir/Ritonavir (LPV/r) 100mg/25mg",
        ],
        DF1: [
            "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]",
            "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
        ],
        FIELDS: [
            "art_consumption"
        ]}]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        facility_name = facility[NAME]
        ratio = 4.6
        non_normalized_field = "Efavirenz (EFV) 200mg [Pack 90]"
        df1_records = self.filter_records(facility_name, combination[DF1])
        df2_records = self.filter_records(facility_name, combination[DF2])
        other_records = self.filter_records(facility_name, [non_normalized_field])
        df1_count = len(df1_records)
        df2_count = len(df2_records)
        df1_values = values_for_records(combination[FIELDS], df1_records)
        df2_values = values_for_records(combination[FIELDS], df2_records)
        other_values = values_for_records([non_normalized_field], other_records)
        sum_df1 = pydash.chain(df1_values).reject(lambda x: x is None).sum().value()
        sum_df2 = pydash.chain(df2_values).reject(lambda x: x is None).sum().value()
        other_sum = pydash.chain(other_values).reject(lambda x: x is None).sum().value()
        adjusted_sum_df1 = (sum_df1 / ratio)
        adjusted_sum_df2 = (sum_df2 / ratio) + other_sum
        total = sum_df2 + sum_df1
        numerator = adjusted_sum_df1
        denominator = adjusted_sum_df2
        result = None
        if abs(adjusted_sum_df1) > abs(adjusted_sum_df2):
            numerator = adjusted_sum_df2
            denominator = adjusted_sum_df1

        if df1_count == 0 or df2_count == 0:
            not_reporting += 1
            result = NOT_REPORTING
        elif total == 0 or (denominator != 0 and 0.7 <= abs(numerator / denominator) <= 1.429):
            yes += 1
            result = YES
        elif denominator != 0 and (abs(numerator / denominator) < 1.0 or abs(numerator / denominator) > 1.429):
            no += 1
            result = NO
        else:
            pass

        return result, no, not_reporting, yes


class NNRTINEWPAEDCheck(NNRTICURRENTADULTSCheck):
    test = NNRTI_NEW_PAED
    combinations = [{
        NAME: 'DEFAULT',
        DF2: [
            "Efavirenz (EFV) 200mg [Pack 90]",
            "Nevirapine (NVP) 50mg [Pack 60]",
            "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
            "Lopinavir/Ritonavir (LPV/r) 100mg/25mg"],
        DF1: [
            "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]",
            "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
        ],
        FIELDS: [
            "estimated_number_of_new_patients",
            "estimated_number_of_new_pregnant_women"
        ]}]


class NNRTINewAdultsCheck(NNRTICURRENTADULTSCheck):
    test = NNRTI_NEW_ADULTS
    combinations = [{
        NAME: 'DEFAULT',
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
        FIELDS: [
            "estimated_number_of_new_patients",
            "estimated_number_of_new_pregnant_women"
        ]}]
