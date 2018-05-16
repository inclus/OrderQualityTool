from django.test import TestCase

from dashboard.checks.builder import DefinitionFactory
from dashboard.checks.check import DBBasedCheckPreview
from dashboard.checks.entities import DefinitionGroup, Definition
from dashboard.checks.tracer import Tracer
from dashboard.models import TracingFormulations


class TestDBBasedCheckPreview(TestCase):

    def test_get_preview_formulations_for_traced_test(self):
        definition = Definition.from_dict(DefinitionFactory().traced().get())
        tracing_formulations = [
            tf.as_dict_obj() for tf in TracingFormulations.objects.all()
        ]
        model = {"id": "Adult", "tracingFormulations": tracing_formulations}
        group = DefinitionGroup.from_dict({"model": model})
        check = DBBasedCheckPreview(definition=definition)
        formulations = check.get_preview_formulations(group)
        self.assertEqual(len(formulations), 7)
        self.assertEqual(
            formulations,
            [
                u"TDF/3TC/EFV (PMTCT)",
                u"TDF/3TC/EFV (ADULT)",
                u"ABC/3TC/LPV/r",
                u"ABC/3TC/EFV",
                u"ABC/3TC/NVP",
                u"ABC/3TC/EFV",
                u"AZT/3TC/EFV",
            ],
        )

    def test_get_preview_formulations_for_other_test(self):
        definition = Definition.from_dict(DefinitionFactory().initial().get())
        group = DefinitionGroup.from_dict(
            {"model": {"id": "Adult"}, "selected_formulations": ["a", "b"]}
        )
        check = DBBasedCheckPreview(definition=definition)
        formulations = check.get_preview_formulations(group)
        self.assertEqual(len(formulations), 2)
        self.assertEqual(formulations, ["a", "b"])

    def test_get_result_key_should_return_default_if_no_tracer_is_given(self):
        definition = Definition.from_dict(DefinitionFactory().initial().get())
        check = DBBasedCheckPreview(definition=definition)
        key = check.get_result_key(None)
        self.assertEqual(key, "DEFAULT")

    def test_get_result_key_should_return_key_for_tracer(self):
        definition = Definition.from_dict(DefinitionFactory().initial().get())
        check = DBBasedCheckPreview(definition=definition)
        key = check.get_result_key(Tracer.F1())
        self.assertEqual(key, "tdf3tcefv-adult")
