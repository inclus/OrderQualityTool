import pydash

from dashboard.data.utils import values_for_records, QCheck, facility_not_reporting, multiple_orders_score
from dashboard.helpers import *


def has_blank_in_fields(fields):
    def func(record):
        values = values_for_records(fields, [record])
        return pydash.some(values, lambda f: f is None)

    return func


class BlanksQualityCheck(QCheck):
    test = ORDER_FORM_FREE_OF_GAPS
    combinations = [{NAME: DEFAULT}]

    fields = [OPENING_BALANCE,
              QUANTITY_RECEIVED,
              ART_CONSUMPTION,
              LOSES_ADJUSTMENTS,
              ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        result = NOT_REPORTING

        number_of_consumption_record_blanks = len(pydash.select(
            values_for_records(self.fields, data[C_RECORDS]), lambda v: v is None))

        if data[C_COUNT] == 0 and data[A_COUNT] == 0 and data[P_COUNT] == 0:
            pass
        elif data[C_COUNT] < 25 or data[A_COUNT] < 22 or data[P_COUNT] < 7:
            result = NO
        elif number_of_consumption_record_blanks > 2:
            result = NO
        else:
            result = YES
        return result


class WebBasedCheck(QCheck):
    test = WEB_BASED
    combinations = [{NAME: DEFAULT}]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        value = data[WEB_PAPER].strip()
        if value and value in [WEB, PAPER]:
            result = value
        else:
            result = NOT_REPORTING
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
