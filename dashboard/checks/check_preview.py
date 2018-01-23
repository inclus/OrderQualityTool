from pydash import py_
from pymaybe import maybe

from dashboard.checks.check import as_float_or_1, get_factored_values, available_aggregations, available_comparisons, \
    cycle_lookups, current
from dashboard.utils import timeit


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
    return py_(collection).flatten().value()[1:]

class DBBasedCheckPreview(object):
    def __init__(self, definition):
        self.definition = definition

    @timeit
    def get_preview_data(self):
        sample_location = self.definition.sample.get('location')
        sample_cycle = self.definition.sample.get('cycle')
        sample_tracer = self.definition.sample.get('tracer')
        groups = []
        for group in self.definition.groups:
            values_for_group = self._group_values_from_db(group, sample_cycle, sample_location, sample_tracer)
            groups.append(values_for_group)
        data = {'groups': groups, 'factored_groups': list()}
        comparison_result, comparison_text = self.compare_results(groups)
        data['result'] = {self.get_result_key(sample_tracer): comparison_result}
        data['resultText'] = comparison_text
        return data

    @timeit
    def _group_values_from_db(self, group, sample_cycle, sample_location, sample_tracer):
        model = group.model.as_model()
        if model:
            values = model.objects.filter(
                name=sample_location['name'],
                cycle=parse_cycle(sample_cycle, group),
                district=sample_location['district'],
                formulation__in=self.get_formulations(group, sample_tracer)
            ).values_list(
                'formulation', *group.selected_fields)

            factored_values = get_factored_values(group.selected_formulations, group.factors, values)
            return {
                "name": group.name,
                "aggregation": group.aggregation.name,
                "values": values,
                "headers": group.selected_fields,
                "has_factors": group.has_factors,
                "factored_values": factored_values,
                "result": self.aggregate_values(group, factored_values)
            }

    def get_formulations(self, group, sample_tracer=None):
        return group.selected_formulations

    def aggregate_values(self, group, values):
        aggregation = available_aggregations.get(group.aggregation.id)
        if aggregation:
            all_values = py_(values).map(lambda x: x[1:]).flatten_deep().value()
            return aggregation(all_values)
        return None

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

    def compare_results(self, groups):
        values = py_(groups).reject(lambda x: x is None).map('factored_values').map(skip_formulation).flatten().reject(lambda x: x is None).value()
        value_count = len(values)
        if self.definition.operator and value_count > 0:
            comparison_class = available_comparisons.get(self.definition.operator.id)
            comparator = comparison_class()
            operator_constant = self.definition.operator_constant

            operator_constant = as_float_or_1(operator_constant)
            gs = py_(groups).reject(lambda x: x is None).value()
            if comparator and gs:
                group1_result = groups[0].get('result')
                group2_result = maybe(groups[1]).or_else({}).get('result')
                comparison_result = comparator.compare(group1_result, group2_result, constant=operator_constant)
                result_text = comparator.text(group1_result, group2_result, operator_constant, comparison_result)
                result = "YES" if comparison_result else "NO"
                return result, result_text
        return "NOT_REPORTING", None

    def get_result_key(self, sample_tracer):
        if sample_tracer and "name" in sample_tracer:
            return sample_tracer.get("name")
        return "DEFAULT"
