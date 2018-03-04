from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.checks.builder import volume_tally_check
from dashboard.checks.legacy.volumetally import VolumeTallyCheck
from dashboard.checks.check import get_check_from_dict
from dashboard.data.entities import LocationData
from dashboard.helpers import *

both_zero = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 0, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 0, EXISTING: 0},
    ],
    P_RECORDS: [
        {FORMULATION: F2_PATIENT_QUERY[0], NEW: 0, EXISTING: 0},
        {FORMULATION: F2_PATIENT_QUERY[1], NEW: 0, EXISTING: 0},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 0},
        {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 0}
    ]

})

patients_blank = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: None, EXISTING: None},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: None, EXISTING: None},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 1000}
    ]

})

consumption_blank = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 100, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 10, EXISTING: 0},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: None}
    ]

})

patients_zero = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 0, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 0, EXISTING: 0},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 1000}
    ]
})

above_30_percent = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 7.1, EXISTING: 7.143},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 7.143, EXISTING: 7.143},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40}
    ]
})

below_30_percent = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 5, EXISTING: 5},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 5, EXISTING: 5},
        {FORMULATION: F2_PATIENT_QUERY[0], NEW: 5, EXISTING: 5},
        {FORMULATION: F2_PATIENT_QUERY[1], NEW: 5, EXISTING: 5},
    ],
    P_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 5, EXISTING: 5},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 5, EXISTING: 5},
        {FORMULATION: F2_PATIENT_QUERY[0], NEW: 5, EXISTING: 5},
        {FORMULATION: F2_PATIENT_QUERY[1], NEW: 5, EXISTING: 5},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40},
        {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 120},
    ]
})

no_data = LocationData.migrate_from_dict({})


class VolumeTallyQualityCheckTestCase(TestCase):
    @parameterized.expand([
        ("no data", no_data, NOT_REPORTING),
        ("both zero", both_zero, YES),
        ("patients blank", patients_blank, NO),
        ("consumption blank", consumption_blank, NO),
        ("patients zero", patients_zero, NO),
        ("0.7", above_30_percent, NO),
        ("one", below_30_percent, YES),
    ])
    def test_f1(self, name, data, expected):
        new_check = get_check_from_dict(volume_tally_check())
        new_check_result = new_check.for_each_facility(data, {"name": "TDF/3TC/EFV (Adult)"})
        self.assertEqual(expected, new_check_result)
        legacy_check = VolumeTallyCheck()
        legacy_check_result = legacy_check.for_each_facility(data, legacy_check.combinations[0])
        self.assertEqual(expected, legacy_check_result)
        self.assertEqual(legacy_check_result, new_check_result)

    @parameterized.expand([
        ("no data", no_data, NOT_REPORTING),
        ("both zero", both_zero, YES),
        ("below_30_percent", below_30_percent, YES),
    ])
    def test_f2(self, name, data, expected):
        new_check = get_check_from_dict(volume_tally_check())
        new_check_result = new_check.for_each_facility(data, {"name": F2, "formulations": F2_PATIENT_QUERY})
        self.assertEqual(expected, new_check_result)
        legacy_check = VolumeTallyCheck()
        legacy_check_result = legacy_check.for_each_facility(data, legacy_check.combinations[1])
        self.assertEqual(expected, legacy_check_result)
        self.assertEqual(legacy_check_result, new_check_result)
