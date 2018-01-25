from django.test import TestCase

from dashboard.checks.check import LessThanComparison, AtLeastNOfTotal


class TestLessThanComparison(TestCase):
    def test_differ_by_less_than_50(self):
        self.assertFalse(LessThanComparison().compare(100, 200, 50))

    def test_dont_differ_by_less_than_50(self):
        self.assertTrue(LessThanComparison().compare(10, 14, 50))
        self.assertFalse(LessThanComparison().compare(0, 3, 50))
        self.assertFalse(LessThanComparison().compare(3, 0, 50))
        self.assertTrue(LessThanComparison().compare(14, 9, 50))
        self.assertTrue(LessThanComparison().compare(10, 10, 50))


class TestAtLeastNOfTotalComparison(TestCase):
    def test_comparison(self):
        self.assertTrue(AtLeastNOfTotal().compare(200, 100, 50))
        self.assertEqual(AtLeastNOfTotal().text(200, 100, 50, True), "200 is at least 50 percent of 100")
        self.assertTrue(AtLeastNOfTotal().compare(10, 14, 10))
        self.assertTrue(AtLeastNOfTotal().compare(14, 9, 50))
        self.assertFalse(AtLeastNOfTotal().compare(10, 60, 50))
        self.assertEqual(AtLeastNOfTotal().text(10, 60, 50, False), "10 is less than 50 percent of 60")

