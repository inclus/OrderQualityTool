from django.test import TestCase

from dashboard.checks.check import LessThanComparison


class TestLessThanComparison(TestCase):
    def test_differ_by_less_than_50(self):
        self.assertFalse(LessThanComparison().compare(100, 200, 50))

    def test_dont_differ_by_less_than_50(self):
        self.assertTrue(LessThanComparison().compare(10, 14, 50))
        self.assertTrue(LessThanComparison().compare(14, 9, 50))
        self.assertTrue(LessThanComparison().compare(10, 10, 50))
