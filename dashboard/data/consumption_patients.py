from collections import defaultdict

import pydash

from dashboard.data.utils import get_patient_total, get_consumption_totals, has_all_blanks, QCheck
from dashboard.helpers import *


class ConsumptionAndPatientsQualityCheck(QCheck):
    test = CONSUMPTION_AND_PATIENTS
    combinations = [{NAME: F1, PATIENT_QUERY: "TDF/3TC/EFV", CONSUMPTION_QUERY: F1_QUERY, RATIO: 2.0,
                     FIELDS: [ART_CONSUMPTION, PMTCT_CONSUMPTION], IS_ADULT: True},
                    {NAME: F2, PATIENT_QUERY: "ABC/3TC", CONSUMPTION_QUERY: F2_QUERY, RATIO: 4.6,
                     FIELDS: [ART_CONSUMPTION], IS_ADULT: False},
                    {NAME: F3, PATIENT_QUERY: "EFV", CONSUMPTION_QUERY: F3_QUERY, RATIO: 1, FIELDS: [ART_CONSUMPTION],
                     IS_ADULT: False}]
    key_cache = defaultdict(dict)

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NOT_REPORTING

 #the df1 and df2  need to pick the correct data for the different formulations.CHECK EXAMPLE ON Bugaya
        facility_name = facility[NAME]
        df1_records = self.get_consumption_records(facility_name, combination[CONSUMPTION_QUERY])
        df2_records = self.get_patient_records(facility_name, combination[PATIENT_QUERY],
                                               combination[IS_ADULT])
        df1_count = len(df1_records)
        df2_count = len(df2_records)

        df2_sum = get_patient_total(df2_records)
        df1_sum = get_consumption_totals(combination[FIELDS], df1_records)
        all_df1_blank = has_all_blanks(df1_records, combination[FIELDS])
        all_df2_blank = has_all_blanks(df2_records, [NEW, EXISTING])
        adjusted_df1_sum = df1_sum / combination[RATIO]
        no, not_reporting, result, yes = self.calculate_score(adjusted_df1_sum, df2_sum,
                                                              df1_count,
                                                              df2_count, yes,
                                                              no,
                                                              not_reporting, result, all_df1_blank,
                                                              all_df2_blank)
        return result, no, not_reporting, yes

    def calculate_score(self, df1_sum, df2_sum, number_of_consumption_records,
                        number_of_patient_records, yes, no, not_reporting, result, all_df1_blank,
                        all_df2_blank):
        numerator = df1_sum
        denominator = df2_sum
        if df2_sum > df1_sum:
            numerator = df2_sum
            denominator = df1_sum
        no_blanks = not all_df1_blank and not all_df2_blank
        both_are_zero = (df1_sum == 0 and df2_sum == 0)
        divisible = denominator != 0
        if number_of_consumption_records == 0 or number_of_patient_records == 0 or (all_df2_blank and all_df1_blank):
            not_reporting += 1
        elif no_blanks and (both_are_zero or (divisible and 0.7 < abs(numerator / denominator) < 1.429)):
            yes += 1
            result = YES
        else:
            no += 1
            result = NO
        return no, not_reporting, result, yes

#Check to see the order limit
    def get_patient_records(self, facility_name, formulation_name, is_adult=True):
        collection = self.report.ads if is_adult else self.report.pds
        records = self.get_records_from_collection(collection, facility_name, self.report.cycle)
        return pydash.chain(records).reject(
                lambda x: formulation_name not in x[FORMULATION]
        ).value()

    def get_records_from_collection(self, collection, facility_name, cycle):
        if facility_name in self.key_cache[cycle]:
            key = self.key_cache[cycle][facility_name]
        else:
            matches = [k for k in collection.keys() if k.lower() in facility_name.lower()]
            if len(matches) > 0:
                key = matches[0]
            else:
                key = facility_name
            self.key_cache[cycle][facility_name] = key
        records = collection[key]
        return records

    def get_consumption_records(self, facility_name, formulation_name):
        records = self.report.cs[facility_name]
        return pydash.chain(records).select(
                lambda x: formulation_name in x[FORMULATION]
        ).value()
