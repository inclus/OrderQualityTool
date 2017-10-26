from unittest import TestCase

from nose_parameterized import parameterized

from dashboard.data.blanks import BlanksQualityCheck
from dashboard.helpers import *


class BlankCheckTestCase(TestCase):
    @parameterized.expand([
        ("pass", 25, 22, 7, YES),
        ("pass", 26, 23, 8, YES),
        ("fail", 24, 22, 7, NO),
        ("fail", 25, 21, 7, NO),
        ("fail", 25, 22, 6, NO),
        ("fail", 1, 1, 1, NO),
        ("n/A", 0, 0, 0, NOT_REPORTING),
    ])
    def test_blank_check(self, name, c_count, a_count, p_count, expected):
        data = {
            WEB_PAPER: "-",
            C_RECORDS:
                [
                    {
                        OPENING_BALANCE: 3,
                        QUANTITY_RECEIVED: 3,
                        COMBINED_CONSUMPTION: 3,
                        LOSES_ADJUSTMENTS: 3,
                        ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3,
                    }],
            C_COUNT: c_count,
            A_COUNT: a_count,
            P_COUNT: p_count
        }
        check = BlanksQualityCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, expected)

    def test_should_fail_if_has_more_than_2_blanks(self):
        data = {
            WEB_PAPER: "-",
            C_RECORDS:
                [
                    {
                        OPENING_BALANCE: 3,
                        QUANTITY_RECEIVED: None,
                        COMBINED_CONSUMPTION: None,
                        LOSES_ADJUSTMENTS: None,
                    }],
            C_COUNT: 25,
            A_COUNT: 22,
            P_COUNT: 7
        }
        check = BlanksQualityCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, NO)
