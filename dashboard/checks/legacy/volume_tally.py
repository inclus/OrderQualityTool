from collections import defaultdict

from dashboard.checks.check import calculate_percentage_variance
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
            NAME: F3, PATIENT_QUERY: F3_PATIENT_QUERY, CONSUMPTION_QUERY: F3_QUERY, RATIO: 1.0,
            FIELDS: [COMBINED_CONSUMPTION],
            IS_ADULT: False
        }]
    key_cache = defaultdict(dict)

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        df1_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
        df2_records = get_patient_records(data, combination[PATIENT_QUERY],
                                          combination[IS_ADULT])
        actual_patient_volumes = get_patient_total(df2_records)
        total_consumption = get_consumption_totals(combination[FIELDS], df1_records)
        all_df1_blank = has_all_blanks(df1_records, combination[FIELDS])
        all_df2_blank = has_all_blanks(df2_records, [NEW, EXISTING])
        both_are_zero = (total_consumption == 0 and actual_patient_volumes == 0)
        if len(df1_records) == 0 and len(df2_records) == 0:
            return NOT_REPORTING
        implied_patient_volume = total_consumption / combination[RATIO]
        no_blanks = not all_df1_blank and not all_df2_blank
        divisible = actual_patient_volumes != 0

        if no_blanks and (both_are_zero or (
                divisible and calculate_percentage_variance(implied_patient_volume, actual_patient_volumes) < 30)):
            return YES
        else:
            return NO
