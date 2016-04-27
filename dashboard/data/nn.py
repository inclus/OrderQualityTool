import pydash

from dashboard.data.utils import QCheck, values_for_records, filter_consumption_records
from dashboard.helpers import *


class NNRTICURRENTADULTSCheck(QCheck):
    test = NNRTI_CURRENT_ADULTS

    combinations = [{
        NAME: DEFAULT,
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
            ART_CONSUMPTION,
            PMTCT_CONSUMPTION
        ],
        RATIO: 2.0,
        SHOW_CONVERSION: True
    }]
    count = 0

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        df1_records = filter_consumption_records(data, combination[DF1])
        df2_records = filter_consumption_records(data, combination[DF2])
        df1_count = len(df1_records)
        df2_count = len(df2_records)
        df1_values = values_for_records(combination.get(FIELDS, []), df1_records)
        df2_values = values_for_records(combination.get(FIELDS, []), df2_records)
        all_df1_fields_are_blank = pydash.every(df1_values, lambda x: x is None) and len(df1_values) > 0
        all_df2_fields_are_blank = pydash.every(df2_values, lambda x: x is None) and len(df2_values) > 0
        sum_df1 = pydash.chain(df1_values).reject(lambda x: x is None).map(float).sum().value()
        sum_df2 = pydash.chain(df2_values).reject(lambda x: x is None).map(float).sum().value()
        if df1_count == 0 or df2_count == 0:
            return NOT_REPORTING
        if all_df1_fields_are_blank or all_df2_fields_are_blank:
            result = NO
        elif (sum_df2 == 0 and sum_df1 == 0) or (sum_df2 != 0 and 0.7 < abs(sum_df1 / sum_df2) < 1.429):
            result = YES
        else:
            result = NO

        return result


class NNRTICURRENTPAEDCheck(NNRTICURRENTADULTSCheck):
    test = NNRTI_CURRENT_PAED
    combinations = [{
        NAME: DEFAULT,

        DF2: [
            "Nevirapine (NVP) 50mg [Pack 60]",
            "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
            "Lopinavir/Ritonavir (LPV/r) 100mg/25mg",
        ],
        DF1: [
            "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]",
            "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
        ],
        OTHER: ["Efavirenz (EFV) 200mg [Pack 90]"],
        FIELDS: [
            ART_CONSUMPTION,
            PMTCT_CONSUMPTION
        ],
        RATIO: 4.6,
        SHOW_CONVERSION: True
    }]

    def for_each_facility(self, data, combination, other_cycle_data={}):
        ratio = combination.get(RATIO)
        df1_records = filter_consumption_records(data, combination[DF1])
        df2_records = filter_consumption_records(data, combination[DF2])
        other_records = filter_consumption_records(data, combination.get(OTHER, []))
        df1_count = len(df1_records)
        df2_count = len(df2_records) + len(other_records)
        df1_values = values_for_records(combination[FIELDS], df1_records)
        df2_values = values_for_records(combination[FIELDS], df2_records)
        other_values = values_for_records(combination[FIELDS], other_records)
        sum_df1 = pydash.chain(df1_values).reject(lambda x: x is None).map(float).sum().value()
        sum_df2 = pydash.chain(df2_values).reject(lambda x: x is None).map(float).sum().value()
        other_sum = pydash.chain(other_values).reject(lambda x: x is None).map(float).sum().value()
        all_df1_fields_are_blank = pydash.every(df1_values, lambda x: x is None) and len(df1_values) > 0
        b1 = pydash.every(df2_values, lambda x: x is None) and len(df2_values) > 0
        b2 = pydash.every(other_values, lambda x: x is None) and len(other_values) > 0
        all_df2_fields_are_blank = b1 and b2

        adjusted_sum_df1 = sum_df1 / ratio

        numerator = adjusted_sum_df1
        denominator = (sum_df2 / ratio) + other_sum
        if df1_count == 0 or df2_count == 0:
            return NOT_REPORTING
        if all_df1_fields_are_blank or all_df2_fields_are_blank:
            result = NO
        elif (sum_df2 == 0 and sum_df1 == 0) or (denominator != 0 and 0.7 < abs(numerator / denominator) < 1.429):
            result = YES
        else:
            result = NO

        return result


class NNRTINEWPAEDCheck(NNRTICURRENTADULTSCheck):
    test = NNRTI_NEW_PAED
    combinations = [{
        NAME: DEFAULT,
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
            ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
            ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN
        ],
        RATIO: 1.0,
        SHOW_CONVERSION: False
    }]


class NNRTINewAdultsCheck(NNRTICURRENTADULTSCheck):
    test = NNRTI_NEW_ADULTS
    combinations = [{
        NAME: DEFAULT,
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
            ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
            ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN
        ],
        RATIO: 1.0,
        SHOW_CONVERSION: False
    }]
