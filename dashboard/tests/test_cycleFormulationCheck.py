from django.test import TestCase

from dashboard.checks.common import CycleFormulationCheck
from dashboard.models import CycleFormulationTestScore


class TestCycleFormulationCheck(TestCase):
    def test_should_not_create_multiple_scores_for_same_cycle_test_and_formulation(self):
        check = CycleFormulationCheck()
        check.test = "THE TEST"
        check.build_cycle_formulation_score("Jan - Feb 2013", "the form", 10, 10, 10, 30)
        check.build_cycle_formulation_score("Jan - Feb 2013", "the form", 10, 15, 15, 40)
        self.assertEqual(1, CycleFormulationTestScore.objects.count())
