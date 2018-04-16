import pydash
from pydash import py_
from pymaybe import maybe

from dashboard.checks.utils import as_float_or_1


class Comparison(object):
    def get_result(self, group_results, definition):
        operator_constant = definition.operator_constant
        operator_constant = as_float_or_1(operator_constant)

        if self.groups_have_adequate_data(group_results):
            group1_aggregate = group_results[0].aggregate
            group2_aggregate = maybe(group_results)[1].aggregate.or_else(None)

            comparison_result = self.as_result(group1_aggregate, group2_aggregate, operator_constant)
            result_text = self.text(group1_aggregate, group2_aggregate, operator_constant)
            return comparison_result, result_text
        return "NOT_REPORTING", None

    def groups_have_adequate_data(self, groups):
        valid_groups = py_(groups).reject(lambda x: x is None).value()
        is_two_cycle = "Previous" in py_(valid_groups).map(lambda group_result: group_result.group.cycle.id).value()
        if is_two_cycle and not py_(valid_groups).every(
                lambda group_result: len(group_result.factored_records) > 0).value():
            return False
        number_of_records = py_(valid_groups).map(
            lambda group_result: group_result.factored_records).flatten().size().value()
        has_adequate_data = number_of_records > 0
        if has_adequate_data:
            return pydash.every(valid_groups, lambda x: x.is_above_threshold())

        return has_adequate_data

    def as_result(self, group1, group2, constant=100.0):
        result = self.compare(group1, group2, constant)
        return "YES" if result else "NO"

    def compare(self, group1, group2, constant=100.0):
        raise NotImplementedError

    def text(self, group1, group2, constant):
        raise NotImplementedError


def calculate_percentage_variance(old_value, new_value):
    old_value = maybe(old_value).or_else(0)
    new_value = maybe(new_value).or_else(0)
    if new_value > old_value:
        temp = new_value
        new_value = old_value
        old_value = temp
    return abs(((float(new_value) - float(old_value)) / old_value) * 100.0)


class PercentageVarianceLessThanComparison(Comparison):

    def compare(self, group1, group2, constant=100.0):
        old_value = maybe(group1).or_else(0)
        new_value = maybe(group2).or_else(0)
        if new_value > old_value:
            temp = new_value
            new_value = old_value
            old_value = temp
        if old_value == 0:
            if new_value == 0:
                return True
            return False
        percentage_variance = calculate_percentage_variance(group1, group2)
        return percentage_variance <= constant

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        template = "%6.1f and %6.1f differ by %s than %s"
        group1 = maybe(group1).or_else(0)
        group2 = maybe(group2).or_else(0)
        return template % (group1, group2, "less" if result else "more", constant)


class PercentageVarianceLessThanComparisonForNNRTI(PercentageVarianceLessThanComparison):
    def groups_have_adequate_data(self, groups):
        denominator = groups[1].aggregate
        if len(groups) > 1 and denominator == 0:
            return False
        return super(PercentageVarianceLessThanComparison, self).groups_have_adequate_data(groups)


class EqualComparison(Comparison):

    def as_result(self, group1, group2, constant=100.0):
        if type(group1) is list:

            if len(group1) < 1 or (group2 is not None and len(group2) < 1):
                return "NOT_REPORTING"
            values = list(group1)
            if group2 is not None:
                values.extend(group2)
            all_zero = pydash.every(values, lambda x: x == 0)
            if all_zero:
                return "YES"

        result = self.compare(group1, group2, constant)
        return "YES" if result else "NO"

    def compare(self, group1, group2, constant=100.0):
        constant = as_float_or_1(constant)
        if type(group1) is list or type(group2) is list:
            return group1 == group2
        return group1 == group2 * constant

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        template = "%s and %s %s equal"
        return template % (group1, group2, "are" if result else "are not")


class NotEqualComparison(EqualComparison):

    def compare(self, group1, group2, constant=100.0):
        parent = super(NotEqualComparison, self).compare(group1, group2, constant)
        result = not parent
        return result


class NoNegativesComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        return py_([group1, group2]).flatten_deep().reject(lambda x: x is None).every(lambda x: x >= 0).value()

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        values = py_([group1, group2]).flatten_deep().reject(lambda x: x is None).value()
        template = "%s of the values %s are negative"
        return template % ("none" if result else "some", values)


def get_all_values_from_non_empty_groups(group1, group2):
    return py_([group1, group2]).filter(lambda x: x is not None).flatten_deep()


class NoBlanksComparison(Comparison):

    def compare(self, group1, group2, constant=100.0):
        return get_all_values_from_non_empty_groups(group1, group2).every(lambda x: x is not None).value()

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        values = get_all_values_from_non_empty_groups(group1, group2).value()
        template = "%s of the values %s are blank"
        return template % ("none" if result else "some", values)


class AtLeastNOfTotal(Comparison):
    def groups_have_adequate_data(self, groups):
        one_group_has_all_blank = py_(groups).reject(lambda x: x is None).some(
            lambda gr: gr.all_values_blank()).value()
        if one_group_has_all_blank:
            return True
        denominator = groups[1].aggregate + groups[0].aggregate
        if len(groups) > 1 and denominator == 0:
            return False
        return super(AtLeastNOfTotal, self).groups_have_adequate_data(groups)

    def compare(self, group1, group2, constant=100.0):
        old_value = maybe(group1).or_else(0)
        new_value = maybe(group2).or_else(0)
        if (new_value + old_value) == 0:
            return False
        total = new_value + old_value
        adjusted_total = (constant / 100.0) * total
        return group1 >= adjusted_total

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        new_value = maybe(group2).or_else(0)
        total = maybe(group1).or_else(0) + new_value
        if total == 0:
            return "denominator value is zero so the check fails"
        template = "%s is %s than %s%% of %s"
        return template % (group1, "more" if result else "less", constant, total)


available_comparisons = {
    "LessThan": PercentageVarianceLessThanComparison,
    "NNRTILessThan": PercentageVarianceLessThanComparisonForNNRTI,
    "AreEqual": EqualComparison,
    "AreNotEqual": NotEqualComparison,
    "NoNegatives": NoNegativesComparison,
    "NoBlanks": NoBlanksComparison,
    "AtLeastNOfTotal": AtLeastNOfTotal,
}
