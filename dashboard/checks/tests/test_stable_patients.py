from django.test import TestCase

from dashboard.checks.builder import stable_patients_check
from dashboard.checks.check import get_check_from_dict
from dashboard.checks.entities import DefinitionGroup, GroupResult
from dashboard.checks.tests.test_comparisons import sum_comparison
from dashboard.checks.tracer import Tracer
from dashboard.data.entities import LocationData, A_RECORDS, FORMULATION


class TestGroupResult(TestCase):

    def test_is_above_threshold(self):
        group = DefinitionGroup(
            name="G2",
            model=None,
            cycle="",
            selected_fields=["consumption"],
            selected_formulations=[],
            sample_formulation_model_overridden={},
            sample_formulation_model_overrides={},
            aggregation=sum_comparison,
            has_factors=None,
            factors=None,
            has_thresholds=True,
            thresholds={
                u"abc3tc-paed": 10, u"efv200-paed": 10, u"tdf3tcefv-adult": "200"
            },
        )
        result = GroupResult(
            group=group,
            values=None,
            factored_records=[],
            aggregate=500.0,
            tracer=Tracer.F1(),
        )
        self.assertEqual(result.is_above_threshold(), True)


class StablePatientsTestCase(TestCase):

    def test_that_aar_passes(self):
        aar = {
            "Current": LocationData.migrate_from_dict(
                {
                    "status": "reporting",
                    A_RECORDS: [
                        {FORMULATION: "TDF/3TC/EFV (PMTCT)", "new": 0.0},
                        {FORMULATION: "TDF/3TC/EFV (PMTCT)", "existing": 7.0},
                        {FORMULATION: "TDF/3TC/EFV (ADULT)", "new": 2.0},
                        {FORMULATION: "TDF/3TC/EFV (ADULT)", "existing": 68.0},
                    ],
                }
            ),
            "Previous": LocationData.migrate_from_dict(
                {
                    "status": "reporting",
                    A_RECORDS: [
                        {FORMULATION: "TDF/3TC/EFV (PMTCT)", "new": 0.0},
                        {FORMULATION: "TDF/3TC/EFV (PMTCT)", "existing": 7.0},
                        {FORMULATION: "TDF/3TC/EFV (ADULT)", "new": 2.0},
                        {FORMULATION: "TDF/3TC/EFV (ADULT)", "existing": 68.0},
                    ],
                }
            ),
        }
        new_check = get_check_from_dict(stable_patients_check())
        new_check_result = new_check.for_each_facility(
            aar["Current"], Tracer.F1(), aar["Previous"]
        )
        self.assertEqual("YES", new_check_result)
