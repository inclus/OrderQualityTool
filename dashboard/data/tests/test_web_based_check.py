from unittest import TestCase

from nose_parameterized import parameterized

from dashboard.data.blanks import WebBasedCheck
from dashboard.helpers import WEB_PAPER, NOT_REPORTING, PAPER, WEB


class WebBasedCheckTestCase(TestCase):
    @parameterized.expand([
        ("Paper", PAPER),
        ("Web", WEB),
        ("", NOT_REPORTING),
        ("-", NOT_REPORTING),
        ("P", NOT_REPORTING),
        ("paper", PAPER),
        ("web", WEB),
    ])
    def test_web_based_check(self, name, expected):
        data = {WEB_PAPER: name}
        check = WebBasedCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, expected)
