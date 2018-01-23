from django.test import TestCase

from dashboard.checks.check import NoNegativesComparison

no_negatives_comparison = NoNegativesComparison().compare


class TestNo_negatives_comparison(TestCase):
    def test_no_negatives_comparison_compares_lists(self):
        result = no_negatives_comparison([1, 2], [121, 12])
        self.assertTrue(result)

    def test_no_negatives_comparison_compares_values(self):
        result = no_negatives_comparison(1, 3)
        self.assertTrue(result)

    def test_can_fail(self):
        self.assertFalse(no_negatives_comparison(1, -3))
        self.assertFalse(no_negatives_comparison(-3, None))

    def test_can_fail_with_list(self):
        result = no_negatives_comparison([11, 212, -3], -3)
        self.assertFalse(result)
