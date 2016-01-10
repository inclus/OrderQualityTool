from collections import defaultdict

import pydash

from dashboard.data.utils import QCheck, values_for_records, build_cycle_formulation_score, facility_not_reporting
from dashboard.helpers import *

THRESHOLD = "threshold"


class TwoCycleQCheck(QCheck):
    def __init__(self, report, other_cycle_report):
        QCheck.__init__(self, report)
        self.other_cycle_report = other_cycle_report
        self.key_cache = defaultdict(dict)

    def get_consumption_records(self, report, facility_name, formulation_name):
        records = report.cs[facility_name]
        return pydash.chain(records).reject(
                lambda x: formulation_name not in x[FORMULATION]
        ).value()

    def get_patient_records(self, report, facility_name, formulation_name, is_adult):
        collection = report.ads if is_adult else report.pds
        records = self.get_records_from_collection(collection, facility_name, report.cycle)
        return pydash.chain(records).select(
                lambda x: formulation_name in x[FORMULATION]
        ).value()

    def get_records_from_collection(self, collection, facility_name, cycle):
        if facility_name in self.key_cache[cycle]:
            key = self.key_cache[cycle][facility_name]
        else:
            matches = [k for k in collection.keys() if k.lower() in facility_name.lower()]
            if len(matches) > 0:
                key = matches[0]
            else:
                key = facility_name
            self.key_cache[cycle][facility_name] = key
        records = collection[key]
        return records


class DIFFERENTORDERSOVERTIMECheck(TwoCycleQCheck):
    test = DIFFERENT_ORDERS_OVER_TIME
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"},
        {NAME: F2, CONSUMPTION_QUERY: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
        {NAME: F3, CONSUMPTION_QUERY: "Efavirenz (EFV) 200mg [Pack 90]"}
    ]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        fields = [OPENING_BALANCE, ART_CONSUMPTION, ESTIMATED_NUMBER_OF_NEW_PATIENTS]

        prev_records = self.get_consumption_records(self.other_cycle_report, facility[NAME], combination[CONSUMPTION_QUERY])
        prev_values = values_for_records(fields, prev_records)

        current_records = self.get_consumption_records(self.report, facility[NAME], combination[CONSUMPTION_QUERY])
        current_values = values_for_records(fields, current_records)

        all_current_values_zero = pydash.every(current_values, lambda x: x == 0)
        all_prev_values_zero = pydash.every(prev_values, lambda x: x == 0)
        all_zero = all_current_values_zero and all_prev_values_zero
        print current_records, prev_records
        if len(current_records) == 0 or len(prev_records) == 0:
            result = NOT_REPORTING
            not_reporting += 1
        elif current_values == prev_values and not all_zero:
            result = NO
            no += 1
        else:
            result = YES
            yes += 1
        return result, no, not_reporting, yes


class CLOSINGBALANCEMATCHESOPENINGBALANCECheck(TwoCycleQCheck):
    test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"},
        {NAME: F2, CONSUMPTION_QUERY: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
        {NAME: F3, CONSUMPTION_QUERY: "Efavirenz (EFV) 200mg [Pack 90]"}
    ]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NOT_REPORTING
        facility_name = facility[NAME]
        prev_records = self.get_consumption_records(self.other_cycle_report, facility_name,
                                                    combination[CONSUMPTION_QUERY])
        current_records = self.get_consumption_records(self.report, facility_name, combination[CONSUMPTION_QUERY])
        closing_balance_values = values_for_records([CLOSING_BALANCE], prev_records)
        opening_balance_values = values_for_records([OPENING_BALANCE], current_records)

        if self.has_no_valid_values(opening_balance_values, closing_balance_values):
            not_reporting += 1
        else:
            no, result, yes = self.compare_values(opening_balance_values[0], closing_balance_values[0], no, result, yes,
                                                  combination[CONSUMPTION_QUERY])
        return result, no, not_reporting, yes

    def compare_values(self, closing_balance, opening_balance, no, result, yes, name):
        if closing_balance != opening_balance:
            no += 1
            result = NO
        else:
            yes += 1
            result = YES
        return no, result, yes

    def has_no_valid_values(self, closing_balance_values, opening_balance_values):
        return len(closing_balance_values) == 0 or len(opening_balance_values) == 0


class STABLECONSUMPTIONCheck(TwoCycleQCheck):
    test = STABLE_CONSUMPTION
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]", THRESHOLD: 20},
        {NAME: F2, CONSUMPTION_QUERY: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]", THRESHOLD: 10},
        {NAME: F3, CONSUMPTION_QUERY: "Efavirenz (EFV) 200mg [Pack 90]", THRESHOLD: 10}
    ]

    def for_each_combination(self, combination, scores):
        facilities = self.report.locs
        yes = 0
        no = 0
        not_reporting = 0
        total_count = 0
        formulation_name = combination[NAME]
        for facility in facilities:
            result, no, not_reporting, yes, total_count = self.for_each_facility_with_count(facility, no, not_reporting, yes, combination, total_count)
            facility['scores'][self.test][formulation_name] = result
        out = build_cycle_formulation_score(formulation_name, yes, no, not_reporting, total_count)
        scores[formulation_name] = out

    def for_each_facility_with_count(self, facility, no, not_reporting, yes, combination, total_count):
        facility_name = facility[NAME]
        prev_records = self.get_consumption_records(self.other_cycle_report, facility_name,
                                                    combination[CONSUMPTION_QUERY])
        current_records = self.get_consumption_records(self.report, facility_name, combination[CONSUMPTION_QUERY])
        threshold = combination[THRESHOLD]
        number_of_consumption_records_prev_cycle = len(prev_records)
        number_of_consumption_records_current_cycle = len(current_records)
        fields = [PMTCT_CONSUMPTION, ART_CONSUMPTION]
        current_consumption = pydash.chain(values_for_records(fields, current_records)).reject(lambda x: x is None).sum().value()
        prev_consumption = pydash.chain(values_for_records(fields, prev_records)).reject(lambda x: x is None).sum().value()
        include_record = current_consumption >= threshold or prev_consumption >= threshold
        result = NOT_REPORTING
        if include_record or facility_not_reporting(facility):
            total_count += 1
            numerator = current_consumption
            denominator = prev_consumption
            if prev_consumption > current_consumption:
                numerator = prev_consumption
                denominator = current_consumption
            if number_of_consumption_records_prev_cycle == 0 or number_of_consumption_records_current_cycle == 0 or facility_not_reporting(facility):
                not_reporting += 1
            elif denominator != 0 and (0.5 <= (numerator / denominator) < 1.5):
                yes += 1
                result = YES
            else:
                no += 1
                result = NO

        return result, no, not_reporting, yes, total_count


class WAREHOUSEFULFILMENTCheck(TwoCycleQCheck):
    test = WAREHOUSE_FULFILMENT
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"},
        {NAME: F2, CONSUMPTION_QUERY: "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"},
        {NAME: F3, CONSUMPTION_QUERY: "Efavirenz (EFV) 200mg [Pack 90]"}
    ]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        facility_name = facility[NAME]
        prev_records = self.get_consumption_records(self.other_cycle_report, facility_name,
                                                    combination[CONSUMPTION_QUERY])
        current_records = self.get_consumption_records(self.report, facility_name, combination[CONSUMPTION_QUERY])
        count_prev = len(prev_records)
        count_current = len(current_records)
        amount_ordered = pydash.chain(values_for_records([PACKS_ORDERED, ], prev_records)).reject(lambda x: x is None).sum().value()
        amount_received = pydash.chain(values_for_records([QUANTITY_RECEIVED], current_records)).reject(lambda x: x is None).sum().value()
        result = NOT_REPORTING
        if count_prev == 0 or count_current == 0:
            not_reporting += 1
        elif amount_ordered == amount_received:
            yes += 1
            result = YES
        else:
            no += 1
            result = NO
        return result, no, not_reporting, yes


class STABLEPATIENTVOLUMESCheck(STABLECONSUMPTIONCheck):
    test = STABLE_PATIENT_VOLUMES
    combinations = [
        {NAME: F1, CONSUMPTION_QUERY: "TDF/3TC/EFV", ADULT: True, THRESHOLD: 10},
        {NAME: F2, CONSUMPTION_QUERY: "ABC/3TC", ADULT: False, THRESHOLD: 5},
        {NAME: F3, CONSUMPTION_QUERY: "EFV", ADULT: False, THRESHOLD: 5}
    ]

    def for_each_facility_with_count(self, facility, no, not_reporting, yes, combination, total_count):
        facility_name = facility[NAME]
        is_adult = combination[ADULT]
        prev_records = self.get_patient_records(self.other_cycle_report, facility_name,
                                                combination[CONSUMPTION_QUERY], is_adult)
        current_records = self.get_patient_records(self.report, facility_name, combination[CONSUMPTION_QUERY], is_adult)
        threshold = combination[THRESHOLD]
        pre_count = len(prev_records)
        current_count = len(current_records)
        current_values = values_for_records([NEW, EXISTING], current_records)
        current_population = pydash.chain(current_values).reject(lambda x: x is None).sum().value()
        prev_values = values_for_records([NEW, EXISTING], prev_records)
        prev_population = pydash.chain(prev_values).reject(lambda x: x is None).sum().value()
        include_record = current_population >= threshold and prev_population >= threshold
        result = NOT_REPORTING
        if include_record or facility_not_reporting(facility):
            total_count += 1
            numerator = current_population
            denominator = prev_population
            if prev_population > current_population:
                numerator = prev_population
                denominator = current_population
            total = current_population + prev_population
            if pre_count == 0 or current_count == 0 or facility_not_reporting(facility):
                not_reporting += 1
            elif current_population == 0 or prev_population == 0 or total < 5 or (0.5 <= numerator / denominator <= 1.5):
                yes += 1
                result = YES
            else:
                no += 1
                result = NO

        return result, no, not_reporting, yes, total_count
