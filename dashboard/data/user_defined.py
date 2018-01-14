from pydash import py_

from dashboard.data.utils import timeit


def as_float_or_1(value):
    try:
        return float(value)
    except ValueError as e:
        return 1
    except TypeError as e:
        return 1


def as_number(value):
    if not value:
        return False, None
    try:
        return True, float(value)
    except ValueError as e:
        return False, None


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


def get_factored_values(formulations, factors, values):
    return py_(values).map(factor_values_by_formulation(formulations, factors)).value()


def sum_aggregation(values):
    return py_(values).reject(lambda x: x is None).sum().value()


def avg_aggregation(values):
    return py_(values).reject(lambda x: x is None).avg().value()


def values_aggregation(values):
    return py_(values).reject(lambda x: x is None).value()


def less_than_comparison(group1, group2, constant=100.0):
    difference = abs(group2 - group1)
    margin = (constant / 100.0) * group1
    return difference < margin


def equal_comparison(group1, group2, constant=1):
    constant = as_float_or_1(constant)
    return group1 == group2 * constant


def no_negatives_comparison(group1, group2, constant=1):
    return py_([group1, group2]).flatten_deep().reject(lambda x: x is None).every(lambda x: x >= 0).value()


available_aggregations = {"SUM": sum_aggregation, "AVG": avg_aggregation, "VALUE": values_aggregation}
available_comparisons = {"LessThan": less_than_comparison, "AreEqual": equal_comparison,
                         "NoNegatives": no_negatives_comparison}


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


class UserDefinedFacilityCheck(object):

    def __init__(self, definition):
        self.definition = definition

    def get_result_for_group(self, group):
        pass

    @timeit
    def get_preview_data(self):
        data = {'groups': list(), 'factored_groups': list()}
        sample_location = self.definition.sample.get('location')
        sample_cycle = self.definition.sample.get('cycle')
        sample_tracer = self.definition.sample.get('tracer')
        groups = []
        for group in self.definition.groups:
            values_for_group = self.get_values_for_group(group, sample_cycle, sample_location, sample_tracer)
            groups.append(values_for_group)
        data['groups'] = groups
        data['result'] = self.compare_results(groups)

        return data

    @timeit
    def get_values_for_group(self, group, sample_cycle, sample_location, sample_tracer):
        model = group.model.as_model()
        if model:
            values = model.objects.filter(
                name=sample_location['name'],
                cycle=sample_cycle,
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
        if self.definition.operator:
            comparator = available_comparisons.get(self.definition.operator.id)
            operator_constant = self.definition.operator_constant

            operator_constant = as_float_or_1(operator_constant)

            if comparator:
                group1_result = groups[0].get('result')
                group2_result = groups[1].get('result')
                result = "YES" if comparator(group1_result, group2_result, constant=operator_constant) else "NO"
                return {"DEFAULT": result}
        return {"DEFAULT": "N\A"}


class UserDefinedFacilityTracedCheck(UserDefinedFacilityCheck):

    def get_formulations(self, group, sample_tracer=None):
        if sample_tracer and "name" in sample_tracer:
            return py_(group.model.tracing_formulations).filter(
                {"name": sample_tracer.get("name")}).first().value().get('formulations')
        return group.model.tracing_formulations[0].get('formulations')
