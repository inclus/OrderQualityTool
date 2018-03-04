from django.test import TestCase

from dashboard.checks.legacy.blanks import MultipleCheck
from dashboard.checks.check import UserDefinedFacilityCheck, get_check_from_dict, get_check
from dashboard.checks.builder import DefinitionFactory, volume_tally_check


class TestCheckLookup(TestCase):
    def test_can_get_check_by_class_name(self):
        definition = DefinitionFactory().based_on_class("dashboard.checks.legacy.blanks.MultipleCheck").getDef()
        check = get_check(definition)
        self.assertIsInstance(check, MultipleCheck)

    def test_can_get_check_by_type(self):
        definition = DefinitionFactory().initial().getDef()
        check = get_check(definition)
        self.assertIsInstance(check, UserDefinedFacilityCheck)


class TestCombinations(TestCase):
    def test_get_combinations(self):
        new_check = get_check_from_dict(volume_tally_check())
        combinations = new_check.get_combinations()
        self.assertListEqual(['TDF/3TC/EFV (Adult)', 'ABC/3TC (Paed)', 'EFV200 (Paed)'], combinations)
        f1_formulations = new_check.get_formulations(new_check.definition.groups[0], combinations[0])
        f2_formulations = new_check.get_formulations(new_check.definition.groups[0], combinations[1])
        f3_formulations = new_check.get_formulations(new_check.definition.groups[0], combinations[2])
        self.assertNotEqual(f1_formulations, f2_formulations)
        self.assertNotEqual(f1_formulations, f3_formulations)
