from collections import defaultdict

from django.test import TestCase
from parameterized import parameterized

from dashboard.checks.builder import stable_consumption_check, stable_patients_check
from dashboard.checks.check import get_check_from_dict
from dashboard.checks.legacy.cycles import StableConsumptionCheck
from dashboard.checks.tasks import run_facility_test
from dashboard.checks.tracer import Tracer
from dashboard.data.entities import LocationData, C_RECORDS, FORMULATION, F1_QUERY, COMBINED_CONSUMPTION, F2_QUERY, YES, \
    NO, Location, NOT_REPORTING
from dashboard.models import Consumption, FacilityTest

passes = {
    "Current": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 50},
            {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 50},
        ]
    }),
    "Previous": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40},
            {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 40},
        ]
    })
}

below_threshold = {
    "Current": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 5},
            {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 5},
        ]
    }),
    "Previous": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 4},
            {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 4},
        ]
    })
}

not_reporting = {
    "Current": LocationData.migrate_from_dict({}),
    "Previous": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40},
            {FORMULATION: F2_QUERY, COMBINED_CONSUMPTION: 40},
        ]
    })
}

f1_current_consumption_zero = {
    "Current": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 0},
        ]
    }),
    "Previous": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40},
        ]
    })
}

f1_consumption_falls_by_50 = {
    "Current": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 30},
        ]
    }),
    "Previous": LocationData.migrate_from_dict({
        'status': 'reporting',
        C_RECORDS: [
            {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 60},
        ]
    })
}


def create_consumption_record(location, formulation, cycle, **fields):
    Consumption.objects.create(
        name=location.facility,
        district=location.district,
        formulation=formulation,
        cycle=cycle, **fields)


class StableConsumptionCheckTestCase(TestCase):
    @parameterized.expand([
        ("YES", passes, YES),
        ("has zero", f1_current_consumption_zero, NOT_REPORTING),
        ("NO", f1_consumption_falls_by_50, YES),
    ])
    def test_that_legacy_gets_same_result_as_new(self, name, scenario, expected):
        legacy_check = StableConsumptionCheck()
        f1_combination = legacy_check.combinations[0]

        new_check = get_check_from_dict(stable_consumption_check())
        new_check_result = new_check.for_each_facility(scenario["Current"], Tracer.F1(),
                                                       scenario["Previous"])
        self.assertEqual(expected, new_check_result)

        legacy_check_result = legacy_check.for_each_facility(scenario["Current"], f1_combination,
                                                             scenario["Previous"])
        self.assertEqual(expected, legacy_check_result)
        self.assertEqual(legacy_check_result, new_check_result)

    @parameterized.expand([
        ("YES", passes, "f1", YES),
        ("NOT_REPORTING", not_reporting, "f1", NOT_REPORTING),
        ("below threshold", below_threshold, "f1", NOT_REPORTING),
        ("YES", passes, "f2", YES),
        ("has zero", f1_current_consumption_zero, "f1", NOT_REPORTING),
        ("NO", f1_consumption_falls_by_50, "f1", YES),
    ])
    def test_that_check_has_same_result_as_preview(self, name, scenario, combination, expected):
        f1_combination = StableConsumptionCheck().combinations[0]
        f2_combination = StableConsumptionCheck().combinations[1]
        combinations = {"f1": f1_combination, "f2": f2_combination}
        combination = combinations[combination]
        new_check = get_check_from_dict(stable_consumption_check())
        new_check_result = new_check.for_each_facility(scenario["Current"], Tracer.F1(),
                                                       scenario["Previous"])
        self.assertEqual(expected, new_check_result)
        current_cycle = "Nov - Dec 2017"
        previous_cycle = "Sep - Oct 2017"
        location = Location(facility="loc1", district="dis1", partner="", warehouse="")
        for record in scenario.get("Current").c_records:
            create_consumption_record(location, record.formulation, current_cycle, consumption=record.consumption)

        for record in scenario.get("Previous").c_records:
            create_consumption_record(location, record.formulation, previous_cycle, consumption=record.consumption)

        data = new_check.get_preview_data({"name": location.facility, "district": location.district}, current_cycle,
                                          combination)
        self.assertEqual(data["result"][combination.key], expected)


class FakeImport(object):

    def __init__(self, locs, cs, ads, pds):
        self.locs = locs
        self.cs = cs
        self.ads = ads
        self.pds = pds


class StablePatients(TestCase):
    def test_check_runs(self):
        scores = defaultdict(lambda: defaultdict(dict))
        test_location = Location(facility=u'St. Michael Kanyike HC III', district=u'Mpigi District', partner='Unknown',
                                 warehouse=u'MAUL', multiple='not', status='Not Reporting')
        locations = [test_location]
        consumption_records = {test_location: []}
        adult_records = {test_location: []}
        paed_records = {test_location: []}
        fake_import = FakeImport(locations, consumption_records, adult_records, paed_records)
        run_facility_test(FacilityTest.objects.get(slug="stable-patients"), fake_import, fake_import, scores)
        self.assertEqual(scores[test_location]['STABLE PATIENTS'],
                         {u'abc3tc-paed': 'NOT_REPORTING', u'efv200-paed': 'NOT_REPORTING',
                          u'tdf3tcefv-adult': 'NOT_REPORTING'})

    def test_check_has_correct_combinations(self):
        new_check = get_check_from_dict(stable_patients_check())
        combinations = new_check.get_combinations()
        self.assertEqual(len(combinations), 3)
        self.assertEqual([tracer.key for tracer in combinations], [u'tdf3tcefv-adult', u'abc3tc-paed', u'efv200-paed'])
