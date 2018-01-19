import pydash

from dashboard.checks.legacy.check import values_for_records, QCheck, facility_not_reporting, multiple_orders_score
from dashboard.helpers import *


class BlanksQualityCheck(QCheck):
    test = ORDER_FORM_FREE_OF_GAPS
    combinations = [{NAME: DEFAULT}]

    fields = [OPENING_BALANCE,
              QUANTITY_RECEIVED,
              COMBINED_CONSUMPTION,
              LOSES_ADJUSTMENTS,
              DAYS_OUT_OF_STOCK]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        result = NOT_REPORTING

        values = values_for_records(self.fields, data.c_records)
        number_of_consumption_record_blanks = len(pydash.select(
            values, lambda v: v is None))

        if data.c_count == 0 and data.a_count == 0 and data.p_count == 0:
            return result
        if data.c_count < 25 or data.a_count < 22 or data.p_count < 7:
            result = NO
        elif number_of_consumption_record_blanks > 2:
            result = NO
        else:
            result = YES
        return result


class IsReportingCheck(QCheck):
    test = REPORTING
    combinations = [{NAME: DEFAULT}]

    def get_combinations(self):
        return [DEFAULT]

    def for_each_facility(self, facility, combination, previous_cycle_data=None):
        return NO if facility_not_reporting(facility) else YES


class MultipleCheck(QCheck):
    test = MULTIPLE_ORDERS
    combinations = [{NAME: DEFAULT}]

    def get_combinations(self):
        return [DEFAULT]

    def for_each_facility(self, facility_data, combination, previous_cycle_data=None):
        return multiple_orders_score(facility_data.location)
