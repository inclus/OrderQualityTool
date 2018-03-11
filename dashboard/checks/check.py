import importlib
from collections import defaultdict

import attr
from pydash import py_, pick
from pymaybe import maybe

from dashboard.checks.aggregations import available_aggregations
from dashboard.checks.comparisons import available_comparisons
from dashboard.checks.utils import as_float_or_1, as_number
from dashboard.checks.entities import Definition, GroupResult, DataRecord
from dashboard.helpers import get_prev_cycle, DEFAULT, YES, NO, N_A
from dashboard.utils import timeit


def factor_values_by_formulation(formulations, factors):
    if not factors:
        factors = {}

    def _p(values):
        values = list(values)
        formulation_name = values[0]
        factor = as_float_or_1(factors.get(formulation_name, 1))
        for index, value in enumerate(values):
            if index != 0:
                is_numerical, numerical_value = as_number(value)
                if numerical_value:
                    values[index] = numerical_value * factor

        return values

    return _p


def as_data_records(fields):
    def _map(item):
        values = [v for i, v in enumerate(pick(attr.asdict(item), fields).values())]
        return DataRecord(formulation=item.formulation, fields=fields, values=values)

    return _map


def previous(cycle):
    return get_prev_cycle(cycle)


def current(cycle):
    return cycle


cycle_lookups = {"Previous": previous, "Currrent": previous}


def get_factored_records(factors, records):
    return py_(records).map(lambda val: val.factor(factors)).value()


CLASS_BASED = "ClassBased"


class DynamicCheckMixin(object):
    def __init__(self, definition):
        self.definition = definition

    def get_formulations(self, group, sample_tracer=None):
        return group.selected_formulations

    def aggregate_values(self, group, values):
        aggregation = available_aggregations.get(group.aggregation.id)
        if aggregation:
            all_values = py_(values).map(lambda x: x.values).flatten_deep().value()
            return aggregation(all_values)
        return None

    def compare_results(self, groups):
        comparison_class = available_comparisons.get(self.definition.operator.id)
        comparator = comparison_class()
        return comparator.get_result(groups, self.definition)


class DBBasedCheckPreview(DynamicCheckMixin):

    @timeit
    def get_preview_data(self, sample_location=None, sample_cycle=None, sample_tracer=None):
        if sample_location is None:
            sample_location = self.definition.sample.get('location')
        if sample_cycle is None:
            sample_cycle = self.definition.sample.get('cycle')
        if sample_tracer is None:
            sample_tracer = self.definition.sample.get('tracer')
        results = []
        for group in self.definition.groups:
            values_for_group = self._group_values_from_db(group, sample_cycle, sample_location, sample_tracer)
            results.append(values_for_group)
        data = {'groups': [r.as_dict() for r in results]}
        comparison_result, comparison_text = self.compare_results(results)
        data['result'] = {self.get_result_key(sample_tracer): comparison_result}
        data['resultText'] = comparison_text
        return data

    @timeit
    def _group_values_from_db(self, group, cycle, sample_location, sample_tracer):
        model = group.model.as_model()
        if group.has_overrides:
            tracer_name = sample_tracer.get("name")
            model_id = group.sample_formulation_model_overrides.get(tracer_name, {}).get("id", None)
            if model_id:
                model = group.model.as_model(model_id)
        if model:
            db_records = model.objects.filter(
                name=sample_location['name'],
                cycle=parse_cycle(cycle, group),
                district=sample_location['district'],
                formulation__in=self.get_formulations(group, sample_tracer)
            ).values_list(
                'formulation', *group.selected_fields)
            records = [DataRecord(formulation=r[0], fields=group.selected_fields, values=r[1:]) for r in db_records]

            factored_values = get_factored_records(group.factors, records)
            return GroupResult(group=group, values=records, factored_records=factored_values,
                               tracer=maybe(sample_tracer).or_else({}).get("name", None),
                               aggregate=self.aggregate_values(group, factored_values))

    @timeit
    def get_locations_and_cycles(self):
        raw_locations = []
        for group in self.definition.groups:
            model = group.model.as_model()
            if model:
                field_filters = build_field_filters(group.selected_fields)
                base_queryset = model.objects.filter(formulation__in=self.get_formulations(group),
                                                     **field_filters)
                raw_locations.extend(
                    base_queryset.order_by('name').values(
                        'name', 'district', 'cycle').distinct())
        locations = py_(raw_locations).uniq().group_by('name').map(as_loc).sort_by("name").value()
        return {"locations": locations}

    def get_result_key(self, sample_tracer):
        if sample_tracer and "name" in sample_tracer:
            return sample_tracer.get("name")
        return "DEFAULT"


class UserDefinedFacilityCheck(DBBasedCheckPreview):

    def get_combinations(self):
        return [DEFAULT]

    def for_each_facility(self, facility_data, combination, other_facility_data=None):
        groups = []
        for group in self.definition.groups:
            values_for_group = self._group_values_from_location_data(group, facility_data, other_facility_data,
                                                                     combination)
            groups.append(values_for_group)
        comparison_result, _ = self.compare_results(groups)
        return comparison_result

    def _group_values_from_location_data(self, group, facility_data, other_facility_data, combination):
        data_source = other_facility_data if group.cycle and group.cycle.id == "Previous" else facility_data
        records = self.get_records_from_data_source(data_source, group)

        if records:
            formulations = self.get_formulations(group, combination)
            data_records = self.get_values_from_records(records, formulations, group.selected_fields)
            factored_records = get_factored_records(group.factors, data_records)
            return GroupResult(group=group, values=data_records, factored_records=factored_records,
                               tracer=combination,
                               aggregate=self.aggregate_values(group, factored_records))

        return GroupResult(group=group, values=[], factored_records=[],
                           tracer=combination,
                           aggregate=None)

    def get_records_from_data_source(self, data_source, group):
        records = group.model.get_records(data_source)
        return records

    def get_values_from_records(self, records, formulations, selected_fields):
        formulations = [f.lower() for f in formulations]
        return py_(records).reject(lambda x: x.formulation.lower() not in formulations).map(
            as_data_records(selected_fields)).value()


class UserDefinedFacilityTracedCheck(UserDefinedFacilityCheck):
    def get_combinations(self):
        return [tracer.get("name") for tracer in self.definition.groups[0].model.tracing_formulations]

    def get_records_from_data_source(self, data_source, group):
        records = group.model.get_records(data_source)
        if group.has_overrides:
            formulations_to_add = defaultdict(set)
            formulations_to_override = []
            for (sample, override_model) in group.sample_formulation_model_overrides.items():
                cleaned_formulation_names = [name.lower() for name in override_model.get("formulations", [])]
                for name in cleaned_formulation_names:
                    formulations_to_add[override_model.get('id')].add(name)
                    formulations_to_override.append(name)
            records = py_(records).reject(lambda x: x.formulation.lower() in formulations_to_override).value()
            for (model, formulations) in formulations_to_add.items():
                get_records = group.model.get_records(data_source, model)
                records_for_override_model = py_(get_records).reject(
                    lambda x: x.formulation.lower() not in formulations).value()
                records.extend(records_for_override_model)
        return records

    def get_formulations(self, group, sample_tracer=None):
        if sample_tracer:
            combination_name = sample_tracer
            if "name" in sample_tracer:
                combination_name = sample_tracer.get("name")

            return py_(group.model.tracing_formulations).find(
                {"name": combination_name}).value().get('formulations')

        return maybe(py_(group.model.tracing_formulations).first().value()).or_else(lambda: {}).get('formulations')


class UserDefinedSingleGroupFacilityCheck(UserDefinedFacilityCheck):

    def compare_results(self, groups):
        if self.definition.operator:
            comparison_class = available_comparisons.get(self.definition.operator.id)
            comparator = comparison_class()
            operator_constant = self.definition.operator_constant

            operator_constant = as_float_or_1(operator_constant)

            if comparator:
                group1_result = groups[0].get('result')
                group2_result = None
                comparison_result = comparator.compare(group1_result, group2_result, constant=operator_constant)
                result_text = comparator.text(group1_result, group2_result, operator_constant, comparison_result)
                result = YES if comparison_result else NO
                return result, result_text
        return N_A, None


testTypes = {
    "FacilityTwoGroups": UserDefinedFacilityCheck,
    "FacilityOneGroup": UserDefinedSingleGroupFacilityCheck,
    "FacilityTwoGroupsAndTracingFormulation": UserDefinedFacilityTracedCheck,
}


def get_check_from_dict(data):
    definition = Definition.from_dict(data)
    return get_check(definition)


def get_check(definition):
    check_type = definition.type.get('id')
    full_class_name = definition.python_class
    if check_type == CLASS_BASED and full_class_name:
        return get_check_by_class(full_class_name)
    dynamic_check = testTypes.get(check_type)(definition)
    return dynamic_check


def get_check_by_class(full_class_name):
    module_name = ".".join(full_class_name.split(".")[:-1])
    class_name = full_class_name.split(".")[-1]
    selected_module = importlib.import_module(module_name)
    check_class = getattr(selected_module, class_name)
    return check_class()


def build_field_filters(selected_fields):
    filter_kwargs = {}
    for field in selected_fields:
        filter_kwargs[field + "__isnull"] = False
    return filter_kwargs


def as_loc(items):
    if len(items) > 0:
        return {
            "name": items[0]['name'],
            "district": items[0]['district'],
            "cycles": [item['cycle'] for item in items]
        }
    else:
        return None


def parse_cycle(sample_cycle, group):
    lookup = group.cycle.id
    lookup = cycle_lookups.get(lookup, current)
    return lookup(sample_cycle)


def skip_formulation(collection):
    if len(collection) > 0 and type(collection[0]) is list:
        return py_(collection).map(skip_formulation).flatten().value()
    return py_(collection).value()[1:]
