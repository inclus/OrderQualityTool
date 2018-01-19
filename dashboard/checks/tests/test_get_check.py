from django.test import TestCase

from dashboard.checks.legacy.blanks import MultipleCheck
from dashboard.checks.user_defined_check import get_check, UserDefinedFacilityCheck
from dashboard.tests.fake_definition import FakeDefinition


class TestCheckLookup(TestCase):
    def test_can_get_check_by_class_name(self):
        definition = FakeDefinition().based_on_class("dashboard.checks.legacy.blanks.MultipleCheck").getDef()
        check = get_check(definition)
        self.assertIsInstance(check, MultipleCheck)

    def test_can_get_check_by_type(self):
        definition = FakeDefinition().initial().getDef()
        check = get_check(definition)
        self.assertIsInstance(check, UserDefinedFacilityCheck)
