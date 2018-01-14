from django.test import TestCase

from dashboard.data.user_defined import less_than_comparison


class TestLess_than_comparison(TestCase):
    def test_differ_by_less_than_50(self):
        self.assertFalse(less_than_comparison(100, 200, 50))

    def test_dont_differ_by_less_than_50(self):
        self.assertTrue(less_than_comparison(10, 14, 50))
        self.assertTrue(less_than_comparison(14, 9, 50))
        self.assertTrue(less_than_comparison(10, 10, 50))
