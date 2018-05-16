from django.test import TestCase

from dashboard.checks.aggregations import avg_aggregation, sum_aggregation


class TestAggregations(TestCase):

    def test_avg_aggregation(self):
        self.assertEqual(avg_aggregation([1, 2, 3]), 2.0)
        self.assertEqual(avg_aggregation([1, 2, 3, None]), 2.0)

    def test_sum_aggregation(self):
        self.assertEqual(sum_aggregation([1, 2, 3]), 6)
        self.assertEqual(sum_aggregation([1, 2, 3, None]), 6)
