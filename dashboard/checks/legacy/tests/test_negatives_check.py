from unittest import TestCase

from nose_parameterized import parameterized

from dashboard.data.entities import LocationData
from dashboard.checks.legacy.negatives import NegativeNumbersQualityCheck
from dashboard.helpers import NOT_REPORTING, YES, C_RECORDS, OPENING_BALANCE, F1_QUERY, FORMULATION, NO

has_no_data = LocationData.migrate_from_dict({})
has_no_negatives = LocationData.migrate_from_dict({
    C_RECORDS: [
        {OPENING_BALANCE: 3, FORMULATION: F1_QUERY}
    ]
})

has_blanks = LocationData.migrate_from_dict({
    C_RECORDS: [
        {OPENING_BALANCE: None, FORMULATION: F1_QUERY}
    ]
})

has_negatives = LocationData.migrate_from_dict({
    C_RECORDS: [
        {OPENING_BALANCE: -3, FORMULATION: F1_QUERY}
    ]
})


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
