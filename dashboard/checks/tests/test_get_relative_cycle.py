from django.test import TestCase

from dashboard.checks.check import parse_cycle
from dashboard.checks.entities import DefinitionGroup


class TestCycleLookup(TestCase):

    def test_that_you_can_get_current_cycle(self):
        group = DefinitionGroup.from_dict({"cycle": {"id": "Current", "name": ""}, "model": {}})
        self.assertEqual(parse_cycle("May - Jun 2016", group), "May - Jun 2016")

    def test_that_you_can_get_previous_cycle(self):
        group = DefinitionGroup.from_dict({"cycle": {"id": "Previous", "name": ""}, "model": {}})
        self.assertEqual(parse_cycle("May - Jun 2016", group), "Mar - Apr 2016")
        self.assertEqual(parse_cycle("Mar - Apr 2016", group), "Jan - Feb 2016")
        self.assertEqual(parse_cycle("Jan - Feb 2016", group), "Nov - Dec 2015")
