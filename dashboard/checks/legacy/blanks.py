import pydash

from dashboard.checks.legacy.check import (
    values_for_records,
    QCheck,
    facility_not_reporting,
    multiple_orders_score,
)
from dashboard.checks.tracer import Tracer
from dashboard.helpers import *
from dashboard.models import MultipleOrderFacility, Score, Consumption


def convert_to_values(record, fields_for_values):
    record_as_dict = record.__dict__
    result = []
    for field in fields_for_values:
        result.append(record_as_dict.get(field))
    return result


class BlanksQualityCheck(QCheck):
    test = ORDER_FORM_FREE_OF_GAPS
    combinations = [{NAME: DEFAULT}]

    def get_combinations(self):
        return [Tracer.Default()]

    fields = [
        OPENING_BALANCE, QUANTITY_RECEIVED, COMBINED_CONSUMPTION, LOSES_ADJUSTMENTS
    ]

    def get_preview_data(self, location, cycle, sample_tracer=None):
        db_records = Consumption.objects.filter(
            name=location.get("name"), district=location.get("district"), cycle=cycle
        )
        fields_for_values = ["formulation"]
        fields_for_values.extend(self.fields)
        values = [convert_to_values(record, fields_for_values) for record in db_records]
        data = {
            "groups": [{"headers": self.fields, "values": values, "name": ""}],
            "result": {self.get_result_key(sample_tracer): ""},
        }
        return data

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        result = NOT_REPORTING

        values = values_for_records(self.fields, data.c_records)
        number_of_consumption_record_blanks = len(
            pydash.filter_(values, lambda v: v is None)
        )
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
        return [Tracer.Default()]

    def for_each_facility(self, facility, combination, previous_cycle_data=None):
        return NO if facility_not_reporting(facility) else YES

    def get_preview_data(self, location, cycle, sample_tracer=None):
        name = location.get("name", None)
        district = location.get("district", None)
        has_scores = Score.objects.filter(
            name=name, district=district, cycle=cycle
        ).exists()
        data = {}
        data["result"] = {
            self.get_result_key(sample_tracer): (YES if has_scores else NO)
        }
        return data


class MultipleCheck(QCheck):
    test = MULTIPLE_ORDERS
    combinations = [{NAME: DEFAULT}]

    def get_combinations(self):
        return [Tracer.Default()]

    def for_each_facility(self, facility_data, combination, previous_cycle_data=None):
        return multiple_orders_score(facility_data.location)

    def get_preview_data(self, location, cycle, sample_tracer=None):
        name = location.get("name", None)
        district = location.get("district", None)
        has_multiple_order = MultipleOrderFacility.objects.filter(
            name=name, district=district, cycle=cycle
        ).exists()
        data = {}
        data["result"] = {
            self.get_result_key(sample_tracer): (NO if has_multiple_order else YES)
        }
        return data
