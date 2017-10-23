import pydash

from dashboard.data.utils import values_for_records, QCheck, facility_not_reporting, multiple_orders_score
from dashboard.helpers import *


class BlanksQualityCheck(QCheck):
    test = ORDER_FORM_FREE_OF_GAPS
    combinations = [{NAME: DEFAULT}]

    fields = [OPENING_BALANCE,
              QUANTITY_RECEIVED,
              COMBINED_CONSUMPTION,
              LOSES_ADJUSTMENTS,
              ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        result = NOT_REPORTING

        values = values_for_records(self.fields, data.get(C_RECORDS, []))
        number_of_consumption_record_blanks = len(pydash.select(
            values, lambda v: v is None))

        c_count_ = data.get(C_COUNT, 0)
        a_count_ = data.get(A_COUNT, 0)
        p_count_ = data.get(P_COUNT, 0)
        if c_count_ == 0 and a_count_ == 0 and p_count_ == 0:
            return result
        if c_count_ < 25 or a_count_ < 22 or p_count_ < 7:
            result = NO
        elif number_of_consumption_record_blanks > 2:
            result = NO
        else:
            result = YES
        return result


class IsReportingCheck(QCheck):
    test = REPORTING
    combinations = [{NAME: DEFAULT}]

    def for_each_facility(self, facility, combination, previous_cycle_data=None):
        return NO if facility_not_reporting(facility) else YES


class MultipleCheck(QCheck):
    test = MULTIPLE_ORDERS
    combinations = [{NAME: DEFAULT}]

    def for_each_facility(self, facility, combination, previous_cycle_data=None):
        return multiple_orders_score(facility)
