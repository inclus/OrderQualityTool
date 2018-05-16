from django.test import TestCase
from parameterized import parameterized

from dashboard.checks.builder import non_repeating_check
from dashboard.checks.legacy.cycles import OrdersOverTimeCheck
from dashboard.checks.check import get_check_from_dict
from dashboard.checks.tracer import Tracer
from dashboard.data.entities import LocationData
from dashboard.helpers import (
    C_RECORDS,
    FORMULATION,
    F1_QUERY,
    OPENING_BALANCE,
    COMBINED_CONSUMPTION,
    YES,
    NOT_REPORTING,
    NO,
    DAYS_OUT_OF_STOCK,
    F1,
)

one_zero = LocationData.migrate_from_dict(
    {
        C_RECORDS: [
            {
                FORMULATION: F1_QUERY,
                OPENING_BALANCE: 12,
                DAYS_OUT_OF_STOCK: 0,
                COMBINED_CONSUMPTION: 4,
            }
        ],
        "status": "reporting",
    }
)

other_formulation = LocationData.migrate_from_dict(
    {
        C_RECORDS: [
            {
                FORMULATION: "the",
                OPENING_BALANCE: 12,
                DAYS_OUT_OF_STOCK: 3,
                COMBINED_CONSUMPTION: 4,
            }
        ],
        "status": "reporting",
    }
)

all_zeros = LocationData.migrate_from_dict(
    {
        C_RECORDS: [
            {
                FORMULATION: F1_QUERY,
                OPENING_BALANCE: 0,
                DAYS_OUT_OF_STOCK: 0,
                COMBINED_CONSUMPTION: 0,
            }
        ],
        "status": "reporting",
    }
)
all_blanks = LocationData.migrate_from_dict(
    {
        C_RECORDS: [
            {
                FORMULATION: F1_QUERY,
                OPENING_BALANCE: None,
                DAYS_OUT_OF_STOCK: None,
                COMBINED_CONSUMPTION: None,
            }
        ],
        "status": "reporting",
    }
)

base = LocationData.migrate_from_dict(
    {
        C_RECORDS: [
            {
                FORMULATION: F1_QUERY,
                OPENING_BALANCE: 12,
                DAYS_OUT_OF_STOCK: 3,
                COMBINED_CONSUMPTION: 4,
            }
        ],
        "status": "reporting",
    }
)


class TestDIFFERENTORDERSOVERTIMECheck(TestCase):

    @parameterized.expand(
        [
            ("same values", base, base, NO),
            ("all zeros", all_zeros, all_zeros, YES),
            ("different scores yes", one_zero, base, YES),
            ("all blanks NA", all_blanks, all_blanks, NOT_REPORTING),
            ("missing scores", other_formulation, base, NOT_REPORTING),
        ]
    )
    def test_check(self, name, data1, data2, expected):
        new_check = get_check_from_dict(non_repeating_check())
        new_check_result = new_check.for_each_facility(data1, Tracer.F1(), data2)
        self.assertEqual(expected, new_check_result)
        check = OrdersOverTimeCheck()
        result = check.for_each_facility(data1, check.combinations[0], data2)
        self.assertEqual(expected, result)
