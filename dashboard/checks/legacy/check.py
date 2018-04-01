import attr
import pydash

from dashboard.helpers import NEW, EXISTING, NO, NOT_REPORTING, YES


def reduce_to_values(records):
    def func(total, field):
        as_dicts = map(attr.asdict, records)
        total.extend(pydash.pluck(as_dicts, field))
        return total

    return func


def values_for_records(fields, records):
    return pydash.reduce_(fields, reduce_to_values(records), [])


def as_float(value):
    try:
        return float(value)
    except ValueError as e:
        return 0.0


def get_consumption_totals(fields, records):
    return pydash.chain(values_for_records(fields, records)).reject(
        lambda x: x is None).map(as_float).sum().value()


def get_patient_total(records):
    return get_consumption_totals([NEW, EXISTING], records)


def has_blank(records, fields):
    return pydash.some(values_for_records(fields, records), lambda x: x is None)


def has_all_blanks(records, fields):
    return pydash.every(values_for_records(fields, records), lambda x: x is None)


class QCheck:
    def __init__(self):
        pass

    combinations = []
    test = ""

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        raise NotImplementedError(self.test)

    def get_result_key(self, sample_tracer):
        if sample_tracer:
            return sample_tracer.key
        return "DEFAULT"


def facility_not_reporting(location_data):
    return location_data.location.status.strip().lower() != 'reporting'


def facility_has_single_order(facility):
    not_multiple = facility.multiple.strip().lower() != 'multiple orders'
    return not_multiple


def multiple_orders_score(facility):
    text_value = facility.multiple.strip().lower()
    if 'multiple' in text_value:
        return NO
    elif 'not' in text_value:
        return NOT_REPORTING
    else:
        return YES


def get_records_from_collection(collection, facility_name):
    records = collection.get(facility_name, [])
    return records


def get_consumption_records(data, names):
    lower_case_names = pydash.map_(names, lambda x: x.lower())
    return pydash.chain(data.c_records).filter_(
        lambda x: x.formulation.strip().lower() in lower_case_names
    ).value()


def get_patient_records(data, names, is_adult=True):
    lower_case_names = pydash.map_(names, lambda x: x.lower())
    records = data.a_records if is_adult else data.p_records
    return pydash.chain(records).filter_(
        lambda x: x.formulation.strip().lower() in lower_case_names
    ).value()


def filter_consumption_records(data, formulation_names):
    def filter_func(x):
        for f in formulation_names:
            if f in x.formulation:
                return True
        return False

    return pydash.filter_(data.c_records, filter_func)
