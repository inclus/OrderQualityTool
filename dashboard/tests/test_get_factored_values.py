from django.test import TestCase

from dashboard.views.definition import get_factored_values


class TestGet_factored_values(TestCase):
    def test_get_factored_values(self):
        result = get_factored_values(True, ["new", "existing"], {"new": 2, "existing": 1}, [[1, 3], [2, 3], [0, 0]])
        self.assertEqual(result, [[2, 3], [4, 3], [0, 0]])

    def test_get_factored_values_when_some_fields_are_missing(self):
        result = get_factored_values(True, ["new", "existing"], {"new": 2}, [[1, 3], [2, 3], [0, 0]])
        self.assertEqual(result, [[2, 3], [4, 3], [0, 0]])

    def test_get_factored_values_when_factors_set(self):
        result = get_factored_values(True, ["new", "existing"], {}, [[1, 3], [2, 3], [0, 0]])
        self.assertEqual(result, [[1, 3], [2, 3], [0, 0]])

    def test_get_factored_values_when_factors_set_to_strings(self):
        result = get_factored_values(True, ["new", "existing"], {"new": "Asd", "existing": "a"},
                                     [[1, 3], [2, 3], [0, 0]])
        self.assertEqual(result, [[1, 3], [2, 3], [0, 0]])

    def test_get_factored_values_when_factors_set_to_decimals(self):
        result = get_factored_values(True, ["new", "existing"], {"new": 0.1, "existing": 2.5},
                                     [[1, 3], [2, 3], [0, 0]])
        self.assertEqual(result, [[0.1, 7.5], [0.2, 7.5], [0, 0]])
