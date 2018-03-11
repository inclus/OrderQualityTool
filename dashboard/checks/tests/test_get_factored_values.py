from django.test import TestCase

from dashboard.checks.check import get_factored_records
from dashboard.checks.entities import DataRecord


class TestFactoredValues(TestCase):
    def test_get_factored_values(self):
        result = get_factored_records({"formA": 2, "formB": 1},
                                      [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                       DataRecord.from_list(["formA", 0, 0])])
        self.assertEqual(result,
                         [DataRecord.from_list(["formA", 2.0, 6.0]), DataRecord.from_list(["formB", 2.0, 3.0]),
                          DataRecord.from_list(["formA", 0.0, 0.0])])

    def test_get_factored_values_when_some_fields_are_missing(self):
        result = get_factored_records({"formA": 2},
                                      [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                       DataRecord.from_list(["formA", 0, 0])])
        self.assertEqual(result, [DataRecord.from_list(["formA", 2, 6]), DataRecord.from_list(["formB", 2, 3]),
                                  DataRecord.from_list(["formA", 0, 0])])

    def test_get_factored_values_when_factors_set(self):
        result = get_factored_records({}, [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                           DataRecord.from_list(["formA", 0, 0])])
        self.assertEqual(result, [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                  DataRecord.from_list(["formA", 0, 0])])

    def test_get_factored_values_when_factors_set_to_strings(self):
        result = get_factored_records({"formA": "Asd", "existing": "a"},
                                      [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                       DataRecord.from_list(["formA", 0, 0])])
        self.assertEqual(result, [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                  DataRecord.from_list(["formA", 0, 0])])

    def test_get_factored_values_when_factors_set_to_decimals(self):
        result = get_factored_records({"formA": 0.1, "formB": 2.5},
                                      [DataRecord.from_list(["formA", 1, 3]), DataRecord.from_list(["formB", 2, 3]),
                                       DataRecord.from_list(["formA", 0, 0])])
        self.assertEqual(result,
                         [DataRecord.from_list(["formA", 0.1, 3 * 0.1]), DataRecord.from_list(["formB", 5.0, 7.5]),
                          DataRecord.from_list(["formA", 0, 0])])

    def test_get_factored_values_when_factors_set_to_decimals_d(self):
        result = get_factored_records({"formA": 0.1, "formB": 2.5},
                                      [DataRecord.from_list(["formA", 1, None])])
        self.assertEqual(result, [DataRecord.from_list(["formA", 0.1, None])])
