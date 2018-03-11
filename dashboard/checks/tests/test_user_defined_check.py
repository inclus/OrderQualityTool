from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.checks.builder import DefinitionFactory, guideline_adherence_adult1l_check, no_negatives_check
from dashboard.checks.entities import DefinitionGroup, DataRecord
from dashboard.checks.legacy.adherence import GuidelineAdherenceCheckAdult1L
from dashboard.checks.legacy.negatives import NegativeNumbersQualityCheck
from dashboard.checks.check import UserDefinedFacilityCheck, get_check_from_dict
from dashboard.data.entities import F1_PATIENT_QUERY
from dashboard.data.entities import LocationData
from dashboard.helpers import A_RECORDS, NEW, EXISTING, \
    COMBINED_CONSUMPTION, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN, F1, \
    NOT_REPORTING, YES
from dashboard.helpers import C_RECORDS, OPENING_BALANCE, F1_QUERY, FORMULATION, NO


class UserDefinedCheckTestCase(TestCase):
    def test_check(self):
        has_no_negatives = LocationData.migrate_from_dict({
            C_RECORDS: [
                {OPENING_BALANCE: 3, FORMULATION: F1_QUERY}
            ]
        })
        definition_builder = DefinitionFactory().initial().formulations(F1_QUERY)
        definition_builder.fields("opening_balance", "closing_balance")
        definition_builder.model('Consumption')
        definition_builder.aggregation("VALUE")
        definition_builder.has_no_negatives()
        check = UserDefinedFacilityCheck(definition_builder.getDef())
        result = check.for_each_facility(has_no_negatives, "DEFAULT")
        self.assertEquals(result, 'YES')

    def test__group_values_from_location_data(self):
        check = UserDefinedFacilityCheck(None)
        test_location_data = LocationData.migrate_from_dict({
            C_RECORDS: [
                {OPENING_BALANCE: 3, FORMULATION: F1_QUERY}
            ]
        })
        group = DefinitionGroup.from_dict(
            {"cycle":
                 {"id": "Next", "name": ""},
             "model": {},
             "selected_formulations": [F1_QUERY],
             "selected_fields": [OPENING_BALANCE]
             }
        )
        output = check.get_values_from_records(test_location_data.c_records, group.selected_formulations,
                                               group.selected_fields)
        self.assertEqual(output, [DataRecord.from_list([F1_QUERY, 3], group.selected_fields)])


insufficient_data = LocationData.migrate_from_dict({
    'status': 'reporting',
    A_RECORDS: [
        {FORMULATION: F1_PATIENT_QUERY[0], NEW: 2.5, EXISTING: 2.5},
        {FORMULATION: F1_PATIENT_QUERY[1], NEW: 2.5, EXISTING: 2.5},
    ],
    C_RECORDS: [
        {FORMULATION: F1_QUERY, COMBINED_CONSUMPTION: 40}
    ]
})

no_data = LocationData.migrate_from_dict({
    'status': 'reporting',

    C_RECORDS: [
        {FORMULATION: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]",
         ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 20},
        {FORMULATION: "AZT/3TC 300/150mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40,
         ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 20},
        {FORMULATION: "AZT/3TC/NVP 300/150/200mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40,
         ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 20}
    ]
})
yes_data = LocationData.migrate_from_dict({
    'status': 'reporting',

    C_RECORDS: [
        {FORMULATION: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]",
         ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 50},
        {FORMULATION: "AZT/3TC 300/150mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3,
         ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 2},
        {FORMULATION: "AZT/3TC/NVP 300/150/200mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3,
         ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 2}
    ]
})


class TestGuideLineAdherence(TestCase):
    @parameterized.expand([
        ("insufficient data", insufficient_data, "NOT_REPORTING"),
        ("yes data", yes_data, "YES"),
        ("no data", no_data, "NO"),
    ])
    def test_check_can_handle(self, name, data, expected_result):
        new_check = get_check_from_dict(guideline_adherence_adult1l_check())
        legacy_check = GuidelineAdherenceCheckAdult1L()

        new_check_result = new_check.for_each_facility(data, "DEFAULT")
        legacy_check_result = legacy_check.for_each_facility(data, legacy_check.combinations[0])
        self.assertEqual(legacy_check_result, expected_result)
        self.assertEqual(expected_result, new_check_result)
        self.assertEqual(legacy_check_result, new_check_result)


has_no_data = LocationData.migrate_from_dict({})
has_no_negatives = LocationData.migrate_from_dict({
    C_RECORDS: [
        {OPENING_BALANCE: 3, FORMULATION: F1_QUERY}
    ]
})

has_blanks = LocationData.migrate_from_dict({
    C_RECORDS: [
        {OPENING_BALANCE: None, FORMULATION: F1_QUERY}
    ]
})

has_negatives = LocationData.migrate_from_dict({
    C_RECORDS: [
        {OPENING_BALANCE: -3, FORMULATION: F1_QUERY}
    ]
})


class NegativeCheckTestCase(TestCase):
    @parameterized.expand([
        ("no data", has_no_data, NOT_REPORTING),
        ("no negatives", has_no_negatives, YES),
        ("has negatives", has_negatives, NO),
        # ("has blanks", has_blanks, YES),
    ])
    def test_check(self, name, data, expected):
        new_check = get_check_from_dict(no_negatives_check())
        legacy_check = NegativeNumbersQualityCheck()

        new_check_result = new_check.for_each_facility(data, {"name": F1, "formulations": F1_QUERY})
        legacy_check_result = legacy_check.for_each_facility(data, legacy_check.combinations[0])
        self.assertEqual(legacy_check_result, new_check_result)
        self.assertEqual(expected, new_check_result)
