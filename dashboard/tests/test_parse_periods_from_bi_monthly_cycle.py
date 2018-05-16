from django.test import TestCase
from parameterized import parameterized

from dashboard.tasks import parse_periods_from_bi_monthly_cycle


class TestParsePeriods(TestCase):

    @parameterized.expand(
        [
            ("Jul - Aug 2020", ["202007", "202008"]),
            ("Jul - Aug 2017", ["201707", "201708"]),
            ("Jan - Feb 2016", ["201601", "201602"]),
            ("Nov - Dec 2000", ["200011", "200012"]),
        ]
    )
    def test_parse_periods_from_bi_monthly_cycle(self, input, expected):
        periods = parse_periods_from_bi_monthly_cycle(input)
        self.assertEqual(periods, expected)
