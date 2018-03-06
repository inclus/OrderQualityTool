from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.checks.builder import stable_consumption_check
from dashboard.checks.check import get_check_from_dict
from dashboard.checks.legacy.cycles import StableConsumptionCheck
from dashboard.data.entities import LocationData, C_RECORDS, FORMULATION, F1_QUERY, COMBINED_CONSUMPTION, F2_QUERY, YES, \
    NO, Location
from dashboard.models import Consumption

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

f1_combination = StableConsumptionCheck().combinations[0]
f2_combination = StableConsumptionCheck().combinations[1]


def create_consumption_record(location, formulation, cycle, **fields):
    Consumption.objects.create(
        name=location.facility,
        district=location.district,
        formulation=formulation,
        cycle=cycle, **fields)


class StableConsumptionCheckTestCase(TestCase):
    @parameterized.expand([
        ("YES", passes, YES),
        ("has zero", f1_current_consumption_zero, NO),
        ("NO", f1_consumption_falls_by_50, YES),
    ])
    def test_that_legacy_gets_same_result_as_new(self, name, scenario, expected):
        legacy_check = StableConsumptionCheck()
        f1_combination = legacy_check.combinations[0]

        new_check = get_check_from_dict(stable_consumption_check())
        new_check_result = new_check.for_each_facility(scenario["Current"], f1_combination,
                                                       scenario["Previous"])
        self.assertEqual(expected, new_check_result)

        legacy_check_result = legacy_check.for_each_facility(scenario["Current"], f1_combination,
                                                             scenario["Previous"])
        self.assertEqual(expected, legacy_check_result)
        self.assertEqual(legacy_check_result, new_check_result)

    @parameterized.expand([
        ("YES", passes, f1_combination, YES),
        ("YES", passes, f2_combination, YES),
        ("has zero", f1_current_consumption_zero, f1_combination, NO),
        ("NO", f1_consumption_falls_by_50, f1_combination, YES),
    ])
    def test_that_check_has_same_result_as_preview(self, name, scenario, combination, expected):

        new_check = get_check_from_dict(stable_consumption_check())
        new_check_result = new_check.for_each_facility(scenario["Current"], f1_combination,
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
        self.assertEqual(data["result"][combination["name"]], expected)
