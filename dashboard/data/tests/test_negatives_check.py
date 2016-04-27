from unittest import TestCase

from nose_parameterized import parameterized

from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.helpers import NOT_REPORTING, YES, C_RECORDS, OPENING_BALANCE, F1_QUERY, FORMULATION, NO

has_no_data = {}
has_no_negatives = {
    C_RECORDS: [
        {OPENING_BALANCE: 3, FORMULATION: F1_QUERY}
    ]
}

has_blanks = {
    C_RECORDS: [
        {OPENING_BALANCE: None, FORMULATION: F1_QUERY}
    ]
}

has_negatives = {
    C_RECORDS: [
        {OPENING_BALANCE: -3, FORMULATION: F1_QUERY}
    ]
}


class NegativeCheckTestCase(TestCase):
    @parameterized.expand([
        ("no data", has_no_data, NOT_REPORTING),
        ("no negatives", has_no_negatives, YES),
        ("has negatives", has_negatives, NO),
        ("has blanks", has_blanks, YES),
    ])
    def test_check(self, name, data, expected):
        check = NegativeNumbersQualityCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, expected)
