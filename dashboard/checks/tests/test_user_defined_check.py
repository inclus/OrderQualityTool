from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.checks.entities import DefinitionGroup, Definition
from dashboard.checks.legacy.adherence import GuidelineAdherenceCheckAdult1L
from dashboard.checks.user_defined_check import UserDefinedFacilityCheck, get_check_from_dict
from dashboard.data.entities import LocationData, F1_PATIENT_QUERY
from dashboard.helpers import FORMULATION, F1_QUERY, OPENING_BALANCE, C_RECORDS, A_RECORDS, NEW, EXISTING, \
    COMBINED_CONSUMPTION, ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN
from dashboard.checks.check_builder import DefinitionFactory, guideline_adherence_adult1l_check


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
        output = check.get_values_from_records(test_location_data.c_records, group)
        self.assertEqual(output, [[F1_QUERY, 3]])


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
        {FORMULATION: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 20},
        {FORMULATION: "AZT/3TC 300/150mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 20},
        {FORMULATION: "AZT/3TC/NVP 300/150/200mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 20}
    ]
})
yes_data = LocationData.migrate_from_dict({
    'status': 'reporting',

    C_RECORDS: [
        {FORMULATION: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 40, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 50},
        {FORMULATION: "AZT/3TC 300/150mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 2},
        {FORMULATION: "AZT/3TC/NVP 300/150/200mg", ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS: 3, ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN: 2}
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
        self.assertEqual(legacy_check_result, new_check_result)
        self.assertEqual(expected_result, new_check_result)

