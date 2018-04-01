from collections import defaultdict

from dashboard.checks.comparisons import calculate_percentage_variance
from dashboard.checks.legacy.check import get_consumption_totals, get_patient_total, has_all_blanks, QCheck, \
    get_consumption_records, get_patient_records
from dashboard.checks.tracer import Tracer
from dashboard.helpers import *


class VolumeTallyCheck(QCheck):
    def __init__(self):
        self.test = CONSUMPTION_AND_PATIENTS
        self.combinations = [
            Tracer.F1().with_data({
                RATIO: 2.0,
                FIELDS: [COMBINED_CONSUMPTION], IS_ADULT: True
            }),
            Tracer.F2().with_data({
                RATIO: 4.6,
                FIELDS: [COMBINED_CONSUMPTION], IS_ADULT: False
            }),
            Tracer.F3().with_data({
                RATIO: 1.0,
                FIELDS: [COMBINED_CONSUMPTION],
                IS_ADULT: False
            }),
        ]

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        df1_records = get_consumption_records(data, tracer.consumption_formulations)
        df2_records = get_patient_records(data, tracer.patient_formulations,
                                          tracer.extras[IS_ADULT])
        actual_patient_volumes = get_patient_total(df2_records)
        total_consumption = get_consumption_totals(tracer.extras[FIELDS], df1_records)
        all_df1_blank = has_all_blanks(df1_records, tracer.extras[FIELDS])
        all_df2_blank = has_all_blanks(df2_records, [NEW, EXISTING])
        both_are_zero = (total_consumption == 0 and actual_patient_volumes == 0)
        if len(df1_records) == 0 and len(df2_records) == 0:
            return NOT_REPORTING
        implied_patient_volume = total_consumption / tracer.extras[RATIO]
        no_blanks = not all_df1_blank and not all_df2_blank
        divisible = actual_patient_volumes != 0

        if no_blanks and (both_are_zero or (
                divisible and calculate_percentage_variance(implied_patient_volume, actual_patient_volumes) < 30)):
            return YES
        else:
            return NO
