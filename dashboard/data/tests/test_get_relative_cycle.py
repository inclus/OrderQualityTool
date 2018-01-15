from django.test import TestCase

from dashboard.data.user_defined import parse_cycle
from dashboard.views.definition import DefinitionGroup


class TestGet_relative_cycle(TestCase):
    def test_that_you_can_get_next_cycle(self):
        group = DefinitionGroup.from_dict({"cycle": {"id": "Next", "name": ""}, "model": {}})
        self.assertEqual(parse_cycle("May - Jun 2016", group), "Jul - Aug 2016")
        self.assertEqual(parse_cycle("Jul - Aug 2016", group), "Sep - Oct 2016")
        self.assertEqual(parse_cycle("Sep - Oct 2016", group), "Nov - Dec 2016")
        self.assertEqual(parse_cycle("Nov - Dec 2016", group), "Jan - Feb 2017")

    def test_that_you_can_get_current_cycle(self):
        group = DefinitionGroup.from_dict({"cycle": {"id": "Current", "name": ""}, "model": {}})
        self.assertEqual(parse_cycle("May - Jun 2016", group), "May - Jun 2016")

    def test_that_you_can_get_previous_cycle(self):
        group = DefinitionGroup.from_dict({"cycle": {"id": "Previous", "name": ""}, "model": {}})
        self.assertEqual(parse_cycle("May - Jun 2016", group), "Mar - Apr 2016")
        self.assertEqual(parse_cycle("Mar - Apr 2016", group), "Jan - Feb 2016")
        self.assertEqual(parse_cycle("Jan - Feb 2016", group), "Nov - Dec 2015")
