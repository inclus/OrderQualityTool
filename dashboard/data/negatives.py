import pydash

from dashboard.data.utils import NAME, CONSUMPTION_QUERY, F1_QUERY, timeit, build_cycle_formulation_score, FORMULATION, \
    values_for_records, \
    QCheck
from dashboard.helpers import CONSUMPTION_AND_PATIENTS, F1, F2, F3, NOT_REPORTING, YES, NO

F1_QUERY = "Efavirenz (TDF/3TC/EFV)"
F2_QUERY = "Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
F3_QUERY = "EFV) 200mg [Pack 90]"


class NegativeNumbersQualityCheck(QCheck):
    test = CONSUMPTION_AND_PATIENTS
    combinations = [{NAME: F1, CONSUMPTION_QUERY: F1_QUERY},
                    {NAME: F2, CONSUMPTION_QUERY: F2_QUERY},
                    {NAME: F3, CONSUMPTION_QUERY: F3_QUERY}]

    fields = ["opening_balance",
              "quantity_received",
              "pmtct_consumption",
              "art_consumption",
              "estimated_number_of_new_pregnant_women",
              "estimated_number_of_new_patients"]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NOT_REPORTING
        facility_name = facility[NAME]
        df1_records = self.get_consumption_records(facility_name, combination[CONSUMPTION_QUERY])
        values = values_for_records(self.fields, df1_records)
        all_cells_not_negative = pydash.every(values,
                                              lambda x: x >= 0 or x is None)
        if len(df1_records) == 0:
            not_reporting += 1
        elif all_cells_not_negative:
            yes += 1
            result = YES
        else:
            no += 1
            result = NO
        return result, no, not_reporting, yes

    def get_consumption_records(self, facility_name, formulation_name):
        records = self.report.cs[facility_name]
        return pydash.chain(records).reject(
            lambda x: formulation_name not in x[FORMULATION]
        ).value()
