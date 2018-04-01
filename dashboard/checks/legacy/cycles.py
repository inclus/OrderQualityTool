import pydash

from dashboard.checks.legacy.check import values_for_records, as_float, QCheck, facility_not_reporting, \
    get_consumption_records, get_patient_records
from dashboard.checks.tracer import Tracer
from dashboard.helpers import *
from dashboard.models import TracingFormulations

THRESHOLD = "threshold"
SLUG = "slug"


class OrdersOverTimeCheck(QCheck):
    def __init__(self):
        self.count = 0
        self.two_cycle = True
        self.test = DIFFERENT_ORDERS_OVER_TIME
        self.combinations = Tracer.from_db()
        self.fields = [OPENING_BALANCE, COMBINED_CONSUMPTION, DAYS_OUT_OF_STOCK]

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        fields = self.fields

        prev_records = get_consumption_records(previous_cycle_data, tracer.consumption_formulations)
        prev_values = values_for_records(fields, prev_records)

        current_records = get_consumption_records(data, tracer.consumption_formulations)
        current_values = values_for_records(fields, current_records)
        all_values = prev_values + current_values
        all_zero = pydash.every(all_values, lambda x: x == 0)
        all_blanks = pydash.every(all_values, lambda x: x is None)
        result = NOT_REPORTING

        if len(current_records) == 0 or len(prev_records) == 0 or all_blanks:
            return result
        if current_values != prev_values or all_zero:
            result = YES
        else:
            result = NO
        return result


class BalancesMatchCheck(QCheck):
    def __init__(self):
        self.count = 0
        self.two_cycle = True
        self.test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE
        self.combinations = Tracer.from_db()

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        result = NOT_REPORTING
        prev_records = get_consumption_records(previous_cycle_data,
                                               tracer.consumption_formulations)
        current_records = get_consumption_records(data, tracer.consumption_formulations)
        closing_balance_values = values_for_records([CLOSING_BALANCE], prev_records)
        opening_balance_values = values_for_records([OPENING_BALANCE], current_records)

        if not self.has_no_valid_values(opening_balance_values, closing_balance_values):
            result = self.compare_values(opening_balance_values[0], closing_balance_values[0])
        return result

    def compare_values(self, closing_balance, opening_balance):
        if closing_balance != opening_balance:
            result = NO
        else:
            result = YES
        return result

    def has_no_valid_values(self, closing_balance_values, opening_balance_values):
        return len(closing_balance_values) == 0 or len(opening_balance_values) == 0


class StableConsumptionCheck(QCheck):
    def __init__(self):
        self.two_cycle = True
        self.test = STABLE_CONSUMPTION
        self.fields = [COMBINED_CONSUMPTION]
        self.combinations = [
            Tracer.F1().with_data({THRESHOLD: 20}),
            Tracer.F2().with_data({THRESHOLD: 10}),
            Tracer.F3().with_data({THRESHOLD: 10}),
        ]

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        prev_records = get_consumption_records(previous_cycle_data, tracer.consumption_formulations)
        current_records = get_consumption_records(data, tracer.consumption_formulations)
        threshold = tracer.extras[THRESHOLD]
        number_of_consumption_records_prev_cycle = len(prev_records)
        number_of_consumption_records_current_cycle = len(current_records)
        fields = self.fields
        current_values = values_for_records(fields, current_records)
        current_consumption = pydash.chain(current_values).reject(lambda x: x is None).sum().value()
        prev_values = values_for_records(fields, prev_records)
        prev_consumption = pydash.chain(prev_values).reject(lambda x: x is None).sum().value()
        include_record = current_consumption > threshold or prev_consumption > threshold
        result = NOT_REPORTING
        if number_of_consumption_records_prev_cycle == 0 or number_of_consumption_records_current_cycle == 0:
            return NOT_REPORTING
        if include_record:
            numerator = float(current_consumption)
            denominator = float(prev_consumption)

            if denominator != 0 and (0.5 <= abs(numerator / denominator) <= 1.5):
                result = YES
            else:
                result = NO

        return result


class WarehouseFulfillmentCheck(QCheck):
    def __init__(self):
        self.count = 0
        self.two_cycle = True
        self.test = WAREHOUSE_FULFILMENT
        self.combinations = Tracer.from_db()

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        prev_records = get_consumption_records(previous_cycle_data, tracer.consumption_formulations)
        current_records = get_consumption_records(data, tracer.consumption_formulations)
        count_prev = len(prev_records)
        count_current = len(current_records)
        prev_values = values_for_records([PACKS_ORDERED, ], prev_records)
        current_values = values_for_records([QUANTITY_RECEIVED], current_records)
        current_values_have_blanks = pydash.some(current_values, lambda x: x is None)
        facility_is_not_reporting = facility_not_reporting(data)
        result = NOT_REPORTING
        data_is_insufficient = count_prev < 1 or count_current < 1 or facility_is_not_reporting

        if data_is_insufficient:
            return result
        elif current_values_have_blanks:
            result = NO
        elif prev_values == current_values:
            result = YES
        else:
            result = NO
        return result


class StablePatientVolumesCheck(StableConsumptionCheck):
    def __init__(self):
        self.two_cycle = True
        self.test = STABLE_PATIENT_VOLUMES
        self.fields = [NEW, EXISTING]
        self.combinations = [
            Tracer.F1().with_data({ADULT: True, THRESHOLD: 10}),
            Tracer.F2().with_data({ADULT: False, THRESHOLD: 5}),
            Tracer.F3().with_data({ADULT: False, THRESHOLD: 5}),
        ]

    def for_each_facility(self, data, tracer, previous_cycle_data=None):
        is_adult = tracer.extras[ADULT]
        prev_records = get_patient_records(previous_cycle_data,
                                           tracer.patient_formulations, is_adult)
        current_records = get_patient_records(data, tracer.patient_formulations, is_adult)

        data_is_sufficient = len(prev_records) > 0 and len(current_records) > 0

        if not data_is_sufficient:
            return NOT_REPORTING

        current_population = self.calculate_sum(current_records)
        prev_population = self.calculate_sum(prev_records)

        threshold = tracer.extras[THRESHOLD]

        include_record = (current_population > threshold or prev_population > threshold)
        result = NOT_REPORTING
        if include_record:
            if float(prev_population) != 0 and 0.5 < abs(float(current_population) / float(prev_population)) < 1.5:
                result = YES
            else:
                result = NO
        return result

    def calculate_sum(self, current_records):
        return pydash.chain(values_for_records(self.fields, current_records)).reject(
            lambda x: x is None).map(as_float).sum().value()
