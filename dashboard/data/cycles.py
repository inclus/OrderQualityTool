import pydash

from dashboard.data.utils import QCheck, NAME, CONSUMPTION_QUERY, FORMULATION, values_for_records
from dashboard.helpers import DIFFERENT_ORDERS_OVER_TIME, NO, YES, CLOSING_BALANCE_MATCHES_OPENING_BALANCE, \
    STABLE_CONSUMPTION, WAREHOUSE_FULFILMENT, STABLE_PATIENT_VOLUMES, F1, F2, F3, NOT_REPORTING


class TwoCycleQCheck(QCheck):
    def __init__(self, report, other_cycle_report):
        QCheck.__init__(self, report)
        self.other_cycle_report = other_cycle_report


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

    def get_consumption_records(self, report, facility_name, formulation_name):
        records = report.cs[facility_name]
        return pydash.chain(records).reject(
            lambda x: formulation_name not in x[FORMULATION]
        ).value()

    def has_no_valid_values(self, closing_balance_values, opening_balance_values):
        return len(closing_balance_values) == 0 or len(opening_balance_values) == 0


class STABLECONSUMPTIONCheck(TwoCycleQCheck):
    test = STABLE_CONSUMPTION
    combinations = [{NAME: 'DEFAULT'}]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NO if facility['status'].strip() != 'Reporting' else YES
        if result == NO:
            no += 1
        else:
            yes += 1
        return result, no, not_reporting, yes


class WAREHOUSEFULFILMENTCheck(TwoCycleQCheck):
    test = WAREHOUSE_FULFILMENT
    combinations = [{NAME: 'DEFAULT'}]

    def for_each_facility(self, facility, no, not_reporting, yes, combination):
        result = NO if facility['status'].strip() != 'Reporting' else YES
        if result == NO:
            no += 1
        else:
            yes += 1
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
