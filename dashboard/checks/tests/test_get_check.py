from django.test import TestCase

from dashboard.checks.legacy.blanks import MultipleCheck
from dashboard.checks.user_defined_check import get_check, UserDefinedFacilityCheck
from dashboard.checks.check_builder import DefinitionFactory


class TestCheckLookup(TestCase):
    def test_can_get_check_by_class_name(self):
        definition = DefinitionFactory().based_on_class("dashboard.checks.legacy.blanks.MultipleCheck").getDef()
        check = get_check(definition)
        self.assertIsInstance(check, MultipleCheck)

    def test_can_get_check_by_type(self):
        definition = DefinitionFactory().initial().getDef()
        check = get_check(definition)
        self.assertIsInstance(check, UserDefinedFacilityCheck)
