import attr
from pydash import py_, pick
from pymaybe import maybe

from dashboard.helpers import get_prev_cycle


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


def sum_aggregation(values):
    return py_(values).reject(lambda x: x is None).sum().value()


def avg_aggregation(values):
    return py_(values).reject(lambda x: x is None).avg().value()


def values_aggregation(values):
    return py_(values).reject(lambda x: x is None).value()


class Comparison(object):
    def compare(self, group1, group2, constant=100.0):
        raise NotImplementedError

    def text(self, group1, group2, constant, result):
        raise NotImplementedError


class LessThanComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        group1 = maybe(group1).or_else(0)
        if group1 == 0:
            return False
        group2 = maybe(group2).or_else(0)
        change = (abs(float(group2) - group1) / group1) * 100.0
        return change < constant

    def text(self, group1, group2, constant, result):
        template = "%d and %d differ by %s than %s"
        group2 = maybe(group2).or_else(0)
        return template % (group1, group2, "less" if result else "more", constant)


class WithinComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        group2 = maybe(group2).or_else(0)
        difference = abs(group2 - group1)
        margin = (constant / 100.0) * group1
        return difference < margin

    def text(self, group1, group2, constant, result):
        template = "%d and %d differ by %s than %s"
        group2 = maybe(group2).or_else(0)
        return template % (group1, group2, "less" if result else "more", constant)


class EqualComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        constant = as_float_or_1(constant)
        if type(group1) is list or type(group2) is list:
            return group1 == group2
        return group1 == group2 * constant

    def text(self, group1, group2, constant, result):
        template = "%s and %s %s equal"
        return template % (group1, group2, "are" if result else "are not")


class NoNegativesComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        return py_([group1, group2]).flatten_deep().reject(lambda x: x is None).every(lambda x: x >= 0).value()

    def text(self, group1, group2, constant, result):
        values = py_([group1, group2]).flatten_deep().reject(lambda x: x is None).value()
        template = "%s of the values %s are negative"
        return template % ("none" if result else "some", values)


class NoBlanksComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        return py_([group1, group2]).flatten_deep().every(lambda x: x is not None).value()

    def text(self, group1, group2, constant, result):
        values = py_([group1, group2]).flatten_deep().value()
        template = "%s of the values %s are blank"
        return template % ("none" if result else "some", values)


class AtLeastNOfTotal(Comparison):
    def compare(self, group1, group2, constant=100.0):
        total = group2 + group1
        adjusted_total = (constant / 100.0) * total
        return group1 >= adjusted_total

    def text(self, group1, group2, constant, result):
        template = "%d %s %d percent of %d"
        return template % (group1, "is at least" if result else "is less than", constant, group2)


available_aggregations = {"SUM": sum_aggregation, "AVG": avg_aggregation, "VALUE": values_aggregation}
available_comparisons = {
    "LessThan": LessThanComparison,
    "AreEqual": EqualComparison,
    "NoNegatives": NoNegativesComparison,
    "NoBlanks": NoBlanksComparison,
    "Within": WithinComparison,
    "AtLeastNOfTotal": AtLeastNOfTotal,
}


def as_values(fields):
    def _map(item):
        values = pick(attr.asdict(item), fields).values()
        output = [item.formulation]
        output.extend(values)
        return output

    return _map


def previous(cycle):
    return get_prev_cycle(cycle)


def current(cycle):
    return cycle


cycle_lookups = {"Previous": previous, "Currrent": previous}


def as_float_or_1(value):
    try:
        return float(value)
    except ValueError as e:
        return 1
    except TypeError as e:
        return 1


def get_factored_values(formulations, factors, values):
    return py_(values).map(factor_values_by_formulation(formulations, factors)).value()
