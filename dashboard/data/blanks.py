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

    def for_each_facility(self, facility, combination):
        result = NOT_REPORTING
        facility_name = facility[NAME]
        c_records = self.report.cs[facility_name]
        a_records = self.report.ads[facility_name]
        p_records = self.report.pds[facility_name]
        cr_count = len(c_records)
        ar_count = len(a_records)
        pr_count = len(p_records)

        number_of_consumption_record_blanks = len(pydash.select(
            values_for_records(self.fields, c_records), lambda v: v is None))

        if cr_count == 0 and ar_count == 0 and pr_count == 0:
            pass
        elif cr_count < 25 or ar_count < 22 or pr_count < 7:
            result = NO
        elif number_of_consumption_record_blanks > 2:
            result = NO
        else:
            result = YES
        return result


class WebBasedCheck(QCheck):
    test = WEB_BASED
    combinations = [{NAME: DEFAULT}]

    def for_each_facility(self, facility, combination):
        value = facility[WEB_PAPER].strip()
        if value and value in [WEB, PAPER]:
            result = value
        else:
            result = NOT_REPORTING
        return result


class IsReportingCheck(QCheck):
    test = REPORTING
    combinations = [{NAME: DEFAULT}]

    def for_each_facility(self, facility, combination):
        return NO if facility_not_reporting(facility) else YES


class MultipleCheck(QCheck):
    test = MULTIPLE_ORDERS
    combinations = [{NAME: DEFAULT}]

    def for_each_facility(self, facility, combination):
        return multiple_orders_score(facility)
