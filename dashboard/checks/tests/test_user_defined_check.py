from django.test import TestCase

from dashboard.checks.entities import DefinitionGroup
from dashboard.checks.user_defined_check import UserDefinedFacilityCheck
from dashboard.data.entities import LocationData
from dashboard.helpers import FORMULATION, F1_QUERY, OPENING_BALANCE, C_RECORDS
from dashboard.tests.fake_definition import FakeDefinition


class UserDefinedCheckTestCase(TestCase):
    def test_check(self):
        has_no_negatives = LocationData.migrate_from_dict({
            C_RECORDS: [
                {OPENING_BALANCE: 3, FORMULATION: F1_QUERY}
            ]
        })
        definition_builder = FakeDefinition().initial().formulations(F1_QUERY)
        definition_builder.fields("opening_balance", "closing_balance")
        definition_builder.model('Consumption')
        definition_builder.aggregation("VALUE")
        definition_builder.has_no_negatives()
        check = UserDefinedFacilityCheck(definition_builder.getDef())
        result = check.for_each_facility(has_no_negatives, "DEFAULT")
        self.assertEquals(result, {'DEFAULT': 'YES'})
    
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
