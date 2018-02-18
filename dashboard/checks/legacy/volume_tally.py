from collections import defaultdict

from dashboard.checks.legacy.check import get_consumption_totals, get_patient_total, has_all_blanks, QCheck, \
    get_consumption_records, get_patient_records
from dashboard.helpers import *


class VolumeTallyCheck(QCheck):
    test = CONSUMPTION_AND_PATIENTS
    combinations = [
        {
            NAME: F1, PATIENT_QUERY: F1_PATIENT_QUERY, CONSUMPTION_QUERY: F1_QUERY, RATIO: 2.0,
            FIELDS: [COMBINED_CONSUMPTION], IS_ADULT: True
        },
        {
            NAME: F2, PATIENT_QUERY: F2_PATIENT_QUERY, CONSUMPTION_QUERY: F2_QUERY, RATIO: 4.6,
            FIELDS: [COMBINED_CONSUMPTION], IS_ADULT: False
        },
        {
            NAME: F3, PATIENT_QUERY: F3_PATIENT_QUERY, CONSUMPTION_QUERY: F3_QUERY, RATIO: 1.0, FIELDS: [COMBINED_CONSUMPTION],
            IS_ADULT: False
        }]
    key_cache = defaultdict(dict)

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        df1_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
        df2_records = get_patient_records(data, combination[PATIENT_QUERY],
                                          combination[IS_ADULT])
        df2_sum = get_patient_total(df2_records)
        df1_sum = get_consumption_totals(combination[FIELDS], df1_records)
        all_df1_blank = has_all_blanks(df1_records, combination[FIELDS])
        all_df2_blank = has_all_blanks(df2_records, [NEW, EXISTING])
        both_are_zero = (df1_sum == 0 and df2_sum == 0)
        if len(df1_records) == 0 and len(df2_records) == 0:
            return NOT_REPORTING
        adjusted_df1_sum = df1_sum / combination[RATIO]
        no_blanks = not all_df1_blank and not all_df2_blank
        divisible = df2_sum != 0
        if no_blanks and (both_are_zero or (divisible and 0.7 < float(adjusted_df1_sum) / float(df2_sum) < 1.429)):
            return YES
        else:
            return NO
