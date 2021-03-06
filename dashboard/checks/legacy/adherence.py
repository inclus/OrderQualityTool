import pydash

from dashboard.checks.legacy.check import (
    values_for_records,
    QCheck,
    facility_not_reporting,
    filter_consumption_records,
)
from dashboard.checks.tracer import Tracer
from dashboard.helpers import *


class GuidelineAdherenceCheckAdult1L(QCheck):

    def __init__(self):
        QCheck.__init__(self)
        self.test = GUIDELINE_ADHERENCE_ADULT_1L
        self.combinations = [
            Tracer.Default().with_data(
                {
                    DF2: ["AZT/3TC", "ABC/3TC"],
                    DF1: ["TDF/3TC"],
                    RATIO: 0.80,
                    FIELDS: [
                        ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
                        ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN,
                    ],
                }
            )
        ]

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        ratio = tracer.extras[RATIO]
        df1_records = filter_consumption_records(data, tracer.extras[DF1])
        df2_records = filter_consumption_records(data, tracer.extras[DF2])
        df1_count = len(df1_records)
        df2_count = len(df2_records)
        df1_values = values_for_records(tracer.extras[FIELDS], df1_records)
        df2_values = values_for_records(tracer.extras[FIELDS], df2_records)
        sum_df1 = pydash.chain(df1_values).reject(lambda x: x is None).sum().value()
        sum_df2 = pydash.chain(df2_values).reject(lambda x: x is None).sum().value()
        all_df1_fields_are_blank = pydash.every(df1_values, lambda x: x is None)
        all_df2_fields_are_blank = pydash.every(df2_values, lambda x: x is None)
        return calculate_score(
            df1_count,
            df2_count,
            sum_df1,
            sum_df2,
            ratio,
            all_df1_fields_are_blank,
            all_df2_fields_are_blank,
            facility_not_reporting(data),
        )


class GuidelineAdherenceCheckAdult2L(GuidelineAdherenceCheckAdult1L):

    def __init__(self):
        GuidelineAdherenceCheckAdult1L.__init__(self)
        self.combinations = [
            {
                NAME: DEFAULT,
                DF2: ["Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"],
                DF1: ["Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"],
                RATIO: 0.80,
                FIELDS: [
                    ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
                    ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN,
                ],
            }
        ]
        self.test = GUIDELINE_ADHERENCE_ADULT_2L


class GuidelineAdherenceCheckPaed1L(GuidelineAdherenceCheckAdult1L):

    def __init__(self):
        GuidelineAdherenceCheckAdult1L.__init__(self)
        self.test = GUIDELINE_ADHERENCE_PAED_1L
        self.combinations = [
            {
                NAME: "DEFAULT",
                DF2: [
                    "Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 60mg/30mg/50mg [Pack 60]",
                    "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]",
                ],
                DF1: ["Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"],
                RATIO: 0.80,
                FIELDS: [ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS],
            }
        ]


def calculate_score(
    df1_count,
    df2_count,
    sum_df1,
    sum_df2,
    ratio,
    all_df1_fields_are_blank=False,
    all_df2_fields_are_blank=False,
    facility_is_not_reporting=False,
):
    total = float(sum_df1 + sum_df2)
    has_blanks = (all_df2_fields_are_blank or all_df1_fields_are_blank)
    has_no_records = df1_count == 0 or df2_count == 0
    adjusted_total = (ratio * total)
    df1_is_at_least_adjusted_total = sum_df1 >= adjusted_total
    result = NOT_REPORTING
    if has_no_records or facility_is_not_reporting:
        pass
    elif df1_is_at_least_adjusted_total:
        result = YES
    elif not df1_is_at_least_adjusted_total:
        result = NO
    elif not has_blanks and (sum_df1 == 0 and sum_df2 == 0):
        result = YES
    elif has_blanks:
        result = NO
    return result
