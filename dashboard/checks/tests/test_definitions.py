import json
import os
import pprint

from dictdiffer import diff
from django.test import TestCase
from nose_parameterized import parameterized

from dashboard.models import FacilityTest


class FacilityTestDefinitions(TestCase):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', "test-data.json")
    fixture = open(file_path, "r").read()
    data = json.loads(fixture)
    scenarios = [(sc['fields']['name'], sc) for sc in data if sc['pk']]

    @parameterized.expand(scenarios)
    def test_definitions_match(self, name, check):
        test_obj = FacilityTest.objects.get(name=check['fields']['name'])
        generated_definition = json.loads(test_obj.definition)
        print("---"*10, check['fields']['name'])
        customised_definition = json.loads(check['fields']['definition'])
        ignore_list = {
            'type.calculations',
            'type.comparisons',
            'type.name',
            'type.models',
            'operator.name',
            'python_class',
            ('groups', 0, 'model', 'formulations'),
            ('groups', 1, 'model', 'formulations'),
            ('groups', 0, 'model', 'tracingFormulations'),
            ('groups', 1, 'model', 'tracingFormulations'),
            ('groups', 0, 'model', 'overrideOptions'),
            ('groups', 1, 'model', 'overrideOptions'),
            ('groups', 0, 'model', 'allowOverride'),
            ('groups', 1, 'model', 'allowOverride'),
            ('groups', 0, 'model', 'fields'),
            ('groups', 1, 'model', 'fields'),
            ('groups', 0, 'model', 'selectId'),
            ('groups', 1, 'model', 'selectId'),
            ('groups', 0, 'cycles'),
            ('groups', 1, 'cycles'),
            ('groups', 0, 'aggregation'),
            ('groups', 1, 'aggregation')
        }
        output = list(diff(generated_definition, customised_definition,
                           ignore=ignore_list))
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(output)
        self.assertLess(len(output), 3)

    @parameterized.expand(scenarios)
    def test_descriptions_match(self, name, check):
        self.maxDiff = None
        test_obj = FacilityTest.objects.get(name=check['fields']['name'])
        actual_description = test_obj.description
        expected_description = check['fields']['description']
        self.assertEqual(actual_description, expected_description)

    @parameterized.expand(scenarios)
    def test_short_descriptions_match(self, name, check):
        self.maxDiff = None
        test_obj = FacilityTest.objects.get(name=check['fields']['name'])
        actual_description = test_obj.short_description
        expected_description = check['fields']['short_description']
        self.assertEqual(actual_description, expected_description)
