from django.test import TestCase

from dashboard.data.user_defined import no_negatives_comparison


class TestNo_negatives_comparison(TestCase):
    def test_no_negatives_comparison_compares_lists(self):
        result = no_negatives_comparison([1, 2], [121, 12])
        self.assertTrue(result)

    def test_no_negatives_comparison_compares_values(self):
        result = no_negatives_comparison(1, 3)
        self.assertTrue(result)

    def test_can_fail(self):
        result = no_negatives_comparison(1, -3)
        self.assertFalse(result)

    def test_can_fail_with_list(self):
        result = no_negatives_comparison([11, 212, -3], -3)
        self.assertFalse(result)
