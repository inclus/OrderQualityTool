from django.test import TestCase

from dashboard.data.user_defined import get_factored_values


class TestGet_factored_values(TestCase):
    def test_get_factored_values(self):
        result = get_factored_values(["formA", "formB"], {"formA": 2, "formB": 1},
                                     [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])
        self.assertEqual(result, [["formA", 2, 6], ["formB", 2, 3], ["formA", 0, 0]])

    def test_get_factored_values_when_some_fields_are_missing(self):
        result = get_factored_values(["formA", "formB"], {"formA": 2},
                                     [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])
        self.assertEqual(result, [["formA", 2, 6], ["formB", 2, 3], ["formA", 0, 0]])

    def test_get_factored_values_when_factors_set(self):
        result = get_factored_values(["formA", "formB"], {}, [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])
        self.assertEqual(result, [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])

    def test_get_factored_values_when_factors_set_to_strings(self):
        result = get_factored_values(["formA", "existing"], {"formA": "Asd", "existing": "a"},
                                     [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])
        self.assertEqual(result, [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])

    def test_get_factored_values_when_factors_set_to_decimals(self):
        result = get_factored_values(["formA", "formB"], {"formA": 0.1, "formB": 2.5},
                                     [["formA", 1, 3], ["formB", 2, 3], ["formA", 0, 0]])
        self.assertEqual(result, [["formA", 0.1, 3*0.1], ["formB", 5.0, 7.5], ["formA", 0, 0]])

    def test_get_factored_values_when_factors_set_to_decimals_d(self):
        result = get_factored_values(["formA", "formB"], {"formA": 0.1, "formB": 2.5},
                                     [["formA", 1, None]])
        self.assertEqual(result, [["formA", 0.1, None]])
