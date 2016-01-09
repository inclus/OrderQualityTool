import pydash

from dashboard.data.utils import QCheck, NAME, CONSUMPTION_QUERY, FORMULATION, values_for_records, build_cycle_formulation_score, facility_not_reporting
from dashboard.helpers import DIFFERENT_ORDERS_OVER_TIME, NO, YES, CLOSING_BALANCE_MATCHES_OPENING_BALANCE, \
    STABLE_CONSUMPTION, WAREHOUSE_FULFILMENT, STABLE_PATIENT_VOLUMES, F1, F2, F3, NOT_REPORTING

THRESHOLD = "threshold"


class TwoCycleQCheck(QCheck):
    def __init__(self, report, other_cycle_report):
        QCheck.__init__(self, report)
        self.other_cycle_report = other_cycle_report

    def get_consumption_records(self, report, facility_name, formulation_name):
        records = report.cs[facility_name]
        return pydash.chain(records).reject(
                lambda x: formulation_name not in x[FORMULATION]
        ).value()


class DIFFERENTORDERSOVERTIMECheck(TwoCycleQCheck):
    test = DIFFERENT_ORDERS_OVER_TIME
    combinations = [{NAME: 'DEFAULT'}]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NO if facility['status'].strip() != 'Reporting' else YES
        if result == NO:
            no += 1
        else:
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
        closing_balance_values = values_for_records(['closing_balance'], prev_records)
        opening_balance_values = values_for_records(['opening_balance'], current_records)

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
        current_consumption = pydash.chain(values_for_records(['pmtct_consumption', 'art_consumption'], current_records)).reject(lambda x: x is None).sum().value()
        prev_consumption = pydash.chain(values_for_records(['pmtct_consumption', 'art_consumption'], prev_records)).reject(lambda x: x is None).sum().value()
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
            elif denominator != 0 and (0.5 <= (numerator / denominator) <= 1.5):
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
        amount_ordered = pydash.chain(values_for_records(['packs_ordered', ], prev_records)).reject(lambda x: x is None).sum().value()
        amount_received = pydash.chain(values_for_records(['quantity_received'], current_records)).reject(lambda x: x is None).sum().value()
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


class STABLEPATIENTVOLUMESCheck(TwoCycleQCheck):
    test = STABLE_PATIENT_VOLUMES
    combinations = [{NAME: 'DEFAULT'}]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NO if facility['status'].strip() != 'Reporting' else YES
        if result == NO:
            no += 1
        else:
            yes += 1
        return result, no, not_reporting, yes
