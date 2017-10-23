from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.helpers import *

both_zero = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 0, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 0, EXISTING: 0},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 0}
    ]

}

patients_blank = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: None, EXISTING: None},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: None, EXISTING: None},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 1000}
    ]

}

consumption_blank = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 100, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 10, EXISTING: 0},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: None}
    ]

}

patients_zero = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 0, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 0, EXISTING: 0},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 1000}
    ]
}

point_seven = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 7.1, EXISTING: 7.143},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 7.143, EXISTING: 7.143},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40}
    ]
}

one = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 5, EXISTING: 5},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 5, EXISTING: 5},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40}
    ]
}

one_point_four = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 3.499, EXISTING: 3.499},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 3.499, EXISTING: 3.499},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 20}
    ]
}

two = {
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 2.5, EXISTING: 2.5},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 2.5, EXISTING: 2.5},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40}
    ]
}
no_data = {}


class ConsumptionAndPatientsQualityCheckTestCase(TestCase):
    @parameterized.expand([
        ("no data", no_data, NOT_REPORTING),
        ("both zero", both_zero, YES),
        ("patients blank", patients_blank, NO),
        ("consumption blank", consumption_blank, NO),
        ("patients zero", patients_zero, NO),
        ("0.7", point_seven, YES),
        ("one", one, YES),
        ("1.4", one_point_four, YES),
        ("two", two, NO),
    ])
    def test_check(self, name, data, expected):
        check = ConsumptionAndPatientsQualityCheck()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEquals(result, expected)
