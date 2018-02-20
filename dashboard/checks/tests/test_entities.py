from django.test import TestCase

from dashboard.checks.entities import DefinitionGroup


class TestDefinitionGroup(TestCase):
    def test_has_overrides_if_one_of_the_overrides_is_set(self):
        group_data = {
            "model": {"id": "Paed"},
            "sample_formulation_model_overrides": {"a": {"id": "A", "formulations": ["a", "b"]}}
        }
        group = DefinitionGroup.from_dict(group_data)
        self.assertTrue(group.has_overrides)

    def test_has_no_overrides_if_none_of_the_overrides_is_set(self):
        group_data = {
            "model": {"id": "Paed"},
            "sample_formulation_model_overrides": {"a": ""}
        }
        group = DefinitionGroup.from_dict(group_data)
        self.assertFalse(group.has_overrides)
