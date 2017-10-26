import pydash

from dashboard.data.utils import values_for_records, facility_not_reporting, get_consumption_records, \
    get_patient_records, QCheck
from dashboard.helpers import *

THRESHOLD = "threshold"


class OrdersOverTimeCheck(QCheck):
    count = 0
    two_cycle = True
    test = DIFFERENT_ORDERS_OVER_TIME
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: F1_QUERY},
        {NAME: F2, CONSUMPTION_QUERY: F2_QUERY},
        {NAME: F3, CONSUMPTION_QUERY: F3_QUERY}
    ]
    fields = [OPENING_BALANCE, COMBINED_CONSUMPTION, DAYS_OUT_OF_STOCK]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        fields = self.fields

        prev_records = get_consumption_records(previous_cycle_data, combination[CONSUMPTION_QUERY])
        prev_values = values_for_records(fields, prev_records)

        current_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
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
    two_cycle = True
    test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: F1_QUERY},
        {NAME: F2, CONSUMPTION_QUERY: F2_QUERY},
        {NAME: F3, CONSUMPTION_QUERY: F3_QUERY}
    ]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        result = NOT_REPORTING
        prev_records = get_consumption_records(previous_cycle_data,
                                               combination[CONSUMPTION_QUERY])
        current_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
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
    two_cycle = True
    test = STABLE_CONSUMPTION
    fields = [COMBINED_CONSUMPTION]
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: F1_QUERY, THRESHOLD: 20},
        {NAME: F2, CONSUMPTION_QUERY: F2_QUERY, THRESHOLD: 10},
        {NAME: F3, CONSUMPTION_QUERY: F3_QUERY, THRESHOLD: 10}
    ]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        prev_records = get_consumption_records(previous_cycle_data, combination[CONSUMPTION_QUERY])
        current_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
        threshold = combination[THRESHOLD]
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
    two_cycle = True
    test = WAREHOUSE_FULFILMENT
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: F1_QUERY},
        {NAME: F2, CONSUMPTION_QUERY: F2_QUERY},
        {NAME: F3, CONSUMPTION_QUERY: F3_QUERY}
    ]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        prev_records = get_consumption_records(previous_cycle_data, combination[CONSUMPTION_QUERY])
        current_records = get_consumption_records(data, combination[CONSUMPTION_QUERY])
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
    two_cycle = True
    test = STABLE_PATIENT_VOLUMES
    combinations = [
        {NAME: F1, PATIENT_QUERY: F1_PATIENT_QUERY, ADULT: True, THRESHOLD: 10},
        {NAME: F2, PATIENT_QUERY: ["ABC/3TC/EFV", "ABC/3TC/NVP"], ADULT: False, THRESHOLD: 5},
        {NAME: F3, PATIENT_QUERY: ["ABC/3TC/EFV", "AZT/3TC/EFV"], ADULT: False, THRESHOLD: 5}
    ]
    fields = [NEW, EXISTING]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        is_adult = combination[ADULT]
        prev_records = get_patient_records(previous_cycle_data,
                                           combination[PATIENT_QUERY], is_adult)
        current_records = get_patient_records(data, combination[PATIENT_QUERY], is_adult)

        data_is_sufficient = len(prev_records) > 0 and len(current_records) > 0

        if not data_is_sufficient:
            return NOT_REPORTING

        current_population = pydash.chain(values_for_records(self.fields, current_records)).reject(
            lambda x: x is None).sum().value()
        prev_population = pydash.chain(values_for_records(self.fields, prev_records)).reject(
            lambda x: x is None).sum().value()

        threshold = combination[THRESHOLD]

        include_record = (current_population > threshold or prev_population > threshold)
        result = NOT_REPORTING
        if include_record:
            if float(prev_population) != 0 and 0.5 < abs(float(current_population) / float(prev_population)) < 1.5:
                result = YES
            else:
                result = NO
        return result
