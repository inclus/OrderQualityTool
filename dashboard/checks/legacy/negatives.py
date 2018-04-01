import pydash

from dashboard.checks.legacy.check import values_for_records, QCheck, get_consumption_records
from dashboard.checks.tracer import Tracer
from dashboard.helpers import *


class NegativeNumbersQualityCheck(QCheck):
    def __init__(self):
        self.test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS

        self.combinations = Tracer.from_db()

        self.fields = [OPENING_BALANCE,
                       QUANTITY_RECEIVED,
                       COMBINED_CONSUMPTION,
                       CLOSING_BALANCE,
                       DAYS_OUT_OF_STOCK]

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        df1_records = get_consumption_records(data, tracer.consumption_formulations)
        values = values_for_records(self.fields, df1_records)
        all_cells_not_negative = pydash.every(values, lambda x: x is None or x >= 0)
        if len(df1_records) == 0:
            return NOT_REPORTING
        return YES if all_cells_not_negative else NO
