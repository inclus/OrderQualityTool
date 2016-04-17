import json
import logging
import time

import pydash

from dashboard.helpers import NO, NOT_REPORTING, YES, EXISTING, NEW, FORMULATION, C_RECORDS, A_RECORDS, P_RECORDS

TWO_CYCLE = "two_cycle"

IS_INTERFACE = "is_interface"

logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print ('%r  %2.2f sec' % (method.__name__, te - ts))
        return result

    return timed


def clean_name(row):
    full_name = row[0].value
    replace_template = "_" + row[5].value.strip()
    return full_name.strip().replace(replace_template, "")


def reduce_to_values(records):
    def func(total, field):
        total.extend(pydash.pluck(records, field))
        return total

    return func


def values_for_records(fields, records):
    return pydash.reduce_(fields, reduce_to_values(records), [])


def get_consumption_totals(fields, records):
    return pydash.chain(values_for_records(fields, records)).reject(
        lambda x: x is None).sum().value()


def get_patient_total(records):
    return get_consumption_totals([NEW, EXISTING], records)


def calculate_percentages(no, not_reporting, total_count, yes):
    if total_count > 0:
        yes_rate = float(yes * 100) / float(total_count)
        no_rate = float(no * 100) / float(total_count)
        not_reporting_rate = float(not_reporting * 100) / float(total_count)
    else:
        no_rate = not_reporting_rate = yes_rate = 0
    return no_rate, not_reporting_rate, yes_rate


def build_cycle_formulation_score(formulation, yes, no, not_reporting, total_count):
    no, not_reporting, yes = calculate_percentages(no, not_reporting, total_count, yes)
    return {NO: no, NOT_REPORTING: not_reporting, YES: yes}


def has_blank(records, fields):
    return pydash.some(values_for_records(fields, records), lambda x: x is None)


def has_all_blanks(records, fields):
    return pydash.every(values_for_records(fields, records), lambda x: x is None)


def write_to_disk(report, file_out):
    with open(file_out, "w") as outfile:
        json.dump(report.cs, outfile)
    return report


class QCheck:
    combinations = []
    test = ""

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        raise NotImplementedError(self.test)


def facility_not_reporting(facility):
    return facility.get('status', '').strip().lower() != 'reporting'


def facility_has_single_order(facility):
    not_multiple = facility['Multiple'].strip().lower() != 'multiple orders'
    return not_multiple


def multiple_orders_score(facility):
    text_value = facility.get('Multiple', '').strip().lower()
    if 'multiple' in text_value:
        return NO
    elif 'not' in text_value:
        return NOT_REPORTING
    else:
        return YES


def get_records_from_collection(collection, facility_name):
    records = collection.get(facility_name, [])
    return records


def get_consumption_records(data, formulation_name):
    return pydash.chain(data[C_RECORDS]).reject(
        lambda x: formulation_name.strip().lower() not in x[FORMULATION].lower()
    ).value()


def get_patient_records(data, combinations, is_adult=True):
    lower_case_combinations = pydash.collect(combinations, lambda x: x.lower())
    records = data[A_RECORDS] if is_adult else data[P_RECORDS]
    return pydash.chain(records).select(
        lambda x: x[FORMULATION].strip().lower() in lower_case_combinations
    ).value()


def filter_consumption_records(data, formulation_names):
    def filter_func(x):
        for f in formulation_names:
            if f in x[FORMULATION]:
                return True
        return False

    return pydash.select(data[C_RECORDS], filter_func)
