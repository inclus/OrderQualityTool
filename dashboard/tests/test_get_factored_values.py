from django.test import TestCase

from dashboard.data.user_defined import get_factored_values


class TestGet_factored_values(TestCase):
    def test_get_factored_values(self):
        result = get_factored_values(["new", "existing"], {"new": 2, "existing": 1},
                                     [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])
        self.assertEqual(result, [["ABC", 2, 3], ["ABC", 4, 3], ["ABC", 0, 0]])

    def test_get_factored_values_when_some_fields_are_missing(self):
        result = get_factored_values(["new", "existing"], {"new": 2},
                                     [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])
        self.assertEqual(result, [["ABC", 2, 3], ["ABC", 4, 3], ["ABC", 0, 0]])

    def test_get_factored_values_when_factors_set(self):
        result = get_factored_values(["new", "existing"], {}, [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])
        self.assertEqual(result, [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])

    def test_get_factored_values_when_factors_set_to_strings(self):
        result = get_factored_values(["new", "existing"], {"new": "Asd", "existing": "a"},
                                     [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])
        self.assertEqual(result, [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])

    def test_get_factored_values_when_factors_set_to_decimals(self):
        result = get_factored_values(["new", "existing"], {"new": 0.1, "existing": 2.5},
                                     [["ABC", 1, 3], ["ABC", 2, 3], ["ABC", 0, 0]])
        self.assertEqual(result, [["ABC", 0.1, 7.5], ["ABC", 0.2, 7.5], ["ABC", 0, 0]])

    def test_get_factored_values_when_factors_set_to_decimals_d(self):
        result = get_factored_values(["new", "existing"], {"new": 0.1, "existing": 2.5},
                                     [["ABC", 1, None]])
        self.assertEqual(result, [["ABC", 0.1, None]])
