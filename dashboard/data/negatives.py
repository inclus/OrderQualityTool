import pandas

from dashboard.data.utils import QCheck, get_consumption_records
from dashboard.helpers import *


class NegativeNumbersQualityCheck(QCheck):
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS
    combinations = [{NAME: F1, CONSUMPTION_QUERY: F1_QUERY},
                    {NAME: F2, CONSUMPTION_QUERY: F2_QUERY},
                    {NAME: F3, CONSUMPTION_QUERY: F3_QUERY}]

    fields = [OPENING_BALANCE,
              QUANTITY_RECEIVED,
              COMBINED_CONSUMPTION]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        consumption_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
        consumption_data_frame = pandas.DataFrame.from_dict(consumption_records)
        test_data_frame = consumption_data_frame.loc[:, consumption_data_frame.columns.isin(self.fields)]
        all_values_positive_or_null = ((test_data_frame >= 0) | (pandas.isnull(test_data_frame))).any(
            axis=1)
        if all_values_positive_or_null.empty:
            return NOT_REPORTING
        else:
            return YES if all_values_positive_or_null.bool() else NO
