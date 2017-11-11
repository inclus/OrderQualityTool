from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.data.cycles import StablePatientVolumesCheck
from dashboard.data.entities import LocationData
from dashboard.helpers import *

initial = LocationData.migrate_from_dict({
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 10, EXISTING: 10},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 10, EXISTING: 10},
    ]

})
increased = LocationData.migrate_from_dict({
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 15, EXISTING: 15},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 10, EXISTING: 10},
    ]

})

doubled = LocationData.migrate_from_dict({
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 20, EXISTING: 20},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 20, EXISTING: 20},
    ]

})

zeros = LocationData.migrate_from_dict({
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 0, EXISTING: 0},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 0, EXISTING: 0},
    ]

})
less_than_threshold = LocationData.migrate_from_dict({
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 1, EXISTING: 1},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 1, EXISTING: 1},
    ]

})
no_data = LocationData.migrate_from_dict({})


class PatientStabilityTestCase(TestCase):
    @parameterized.expand([
        ("population same", initial, initial, YES),
        ("population increased", increased, initial, YES),
        ("population to zero", zeros, initial, NO),
        ("population from zero", initial, zeros, NO),
        ("population all zero", zeros, zeros, NOT_REPORTING),
        ("population doubled", doubled, initial, NO),
        ("no data", no_data, no_data, NOT_REPORTING),
        ("less than threshold", less_than_threshold, less_than_threshold, NOT_REPORTING),
    ])
    def test_check(self, name, data, prev_data, expected):
        check = StablePatientVolumesCheck()
        result = check.for_each_facility(data, check.combinations[0], prev_data)
        self.assertEquals(result, expected)
