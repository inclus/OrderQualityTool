import pydash
from pydash import py_
from pymaybe import maybe


class Comparison(object):
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
    return abs(((float(new_value) - float(old_value)) / old_value) * 100.0)


class PercentageVarianceLessThanComparison(Comparison):

    def compare(self, group1, group2, constant=100.0):
        old_value = maybe(group1).or_else(0)
        new_value = maybe(group2).or_else(0)
        if old_value == 0:
            if new_value == 0:
                return True
            return False
        percentage_variance = calculate_percentage_variance(group1, group2)
        return percentage_variance < constant

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        template = "%6.1f and %6.1f differ by %s than %s"
        group1 = maybe(group1).or_else(0)
        group2 = maybe(group2).or_else(0)
        return template % (group1, group2, "less" if result else "more", constant)


class WithinComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        group2 = maybe(group2).or_else(0)
        difference = abs(group2 - group1)
        margin = (constant / 100.0) * group1
        return difference < margin

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        template = "%d and %d differ by %s than %s"
        group2 = maybe(group2).or_else(0)
        return template % (group1, group2, "less" if result else "more", constant)


class EqualComparison(Comparison):

    def as_result(self, group1, group2, constant=100.0):
        if type(group1) is list:

            if len(group1) < 1 or len(group2) < 1:
                return "NOT_REPORTING"
            values = list(group1)
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


class NoBlanksComparison(Comparison):
    def compare(self, group1, group2, constant=100.0):
        return py_([group1, group2]).flatten_deep().every(lambda x: x is not None).value()

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        values = py_([group1, group2]).flatten_deep().value()
        template = "%s of the values %s are blank"
        return template % ("none" if result else "some", values)


class AtLeastNOfTotal(Comparison):
    def compare(self, group1, group2, constant=100.0):
        total = group2 + group1
        adjusted_total = (constant / 100.0) * total
        return group1 >= adjusted_total

    def text(self, group1, group2, constant):
        result = self.compare(group1, group2, constant)
        template = "%d %s %d percent of %d"
        return template % (group1, "is at least" if result else "is less than", constant, group2)


def as_float_or_1(value):
    try:
        return float(value)
    except ValueError as e:
        return 1
    except TypeError as e:
        return 1


available_comparisons = {
    "LessThan": PercentageVarianceLessThanComparison,
    "AreEqual": EqualComparison,
    "AreNotEqual": NotEqualComparison,
    "NoNegatives": NoNegativesComparison,
    "NoBlanks": NoBlanksComparison,
    "Within": WithinComparison,
    "AtLeastNOfTotal": AtLeastNOfTotal,
}