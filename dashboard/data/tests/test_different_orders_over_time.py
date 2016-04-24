from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.data.cycles import OrdersOverTimeCheck
from dashboard.helpers import C_RECORDS, FORMULATION, F1_QUERY, OPENING_BALANCE, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS, ART_CONSUMPTION, YES, NOT_REPORTING, NO

one_zero = {C_RECORDS: [{FORMULATION: F1_QUERY, OPENING_BALANCE: 12, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 0, ART_CONSUMPTION: 4}]}

other_formulation = {C_RECORDS: [{FORMULATION: "the", OPENING_BALANCE: 12, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3, ART_CONSUMPTION: 4}]}

all_zeros = {C_RECORDS: [{FORMULATION: F1_QUERY, OPENING_BALANCE: 0, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 0, ART_CONSUMPTION: 0}]}
all_blanks = {C_RECORDS: [{FORMULATION: F1_QUERY, OPENING_BALANCE: None, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: None, ART_CONSUMPTION: None}]}

base = {C_RECORDS: [{FORMULATION: F1_QUERY, OPENING_BALANCE: 12, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3, ART_CONSUMPTION: 4}]}


class TestDIFFERENTORDERSOVERTIMECheck(TestCase):
    @parameterized.expand([
        ("same values", base, base, NO),
        ("all zeros", all_zeros, all_zeros, YES),
        ("different scores yes", one_zero, base, YES),
        ("all blanks NA", all_blanks, all_blanks, NOT_REPORTING),
        ("missing scores", other_formulation, base, NOT_REPORTING),
    ])
    def test_check(self, name, data1, data2, expected):
        check = OrdersOverTimeCheck()
        result = check.for_each_facility(data1, check.combinations[0], data2)
        self.assertEqual(result, expected)
