from pydash import py_


def as_float_or_1(value):
    try:
        return float(value)
    except ValueError as e:
        return 1


def as_number(value):
    if not value:
        return False, None
    try:
        return True, float(value)
    except ValueError as e:
        return False, None


def factor_values(fields, factors):
    if not factors:
        factors = {}

    def _p(values):
        values = list(values)
        for index, field in enumerate(fields):
            factor = as_float_or_1(factors.get(field, 1))
            is_numerical, numerical_value = as_number(values[index + 1])
            if numerical_value:
                values[index + 1] = numerical_value * factor
        return values

    return _p


def get_factored_values(fields, factors, values):
    return py_(values).map(factor_values(fields, factors)).value()


def sum_aggregation(values):
    return py_(values).sum().value()


def avg_aggregation(values):
    return py_(values).avg().value()


available_aggregations = {"SUM": sum_aggregation, "AVG": avg_aggregation}


class UserDefinedFacilityCheck(object):

    def __init__(self, definition):
        self.definition = definition

    def get_result_for_group(self, group):
        pass

    def get_preview_data(self):
        data = {}
        data['groups'] = list()
        data['factored_groups'] = list()
        sample_location = self.definition.sample.get('location')
        sample_cycle = self.definition.sample.get('cycle')
        for group in self.definition.groups:
            model = group.model.as_model()
            if model:
                for_group = self.get_values_for_group(group, model, sample_cycle, sample_location)
                data['groups'].append(for_group)
        return data

    def get_values_for_group(self, group, model, sample_cycle, sample_location):
        values = model.objects.filter(
            name=sample_location['name'],
            cycle=sample_cycle,
            district=sample_location['district'],
            formulation__in=group.selected_formulations
        ).values_list(
            'formulation', *group.selected_fields)

        factored_values = get_factored_values(group.selected_fields, group.factors, values)
        return {
            "name": group.name,
            "aggregation": group.aggregation.name,
            "values": values,
            "headers": group.selected_fields,
            "has_factors": group.has_factors,
            "factored_values": factored_values,
            "result": self.aggregate_values(group, factored_values)
        }

    def aggregate_values(self, group, values):
        aggregation = available_aggregations.get(group.aggregation.id)
        if aggregation:
            all_values = py_(values).map(lambda x: x[1:]).flatten_deep().value()
            return aggregation(all_values)
        return None
