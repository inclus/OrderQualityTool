from dynamic_preferences.preferences import Section
from dynamic_preferences.types import DecimalPreference, FloatPreference
from dynamic_preferences.registries import global_preferences_registry

quality_tests = Section('Quality_Tests')


@global_preferences_registry.register
class GuidelineAdherenceCheckAdult2LRatio(FloatPreference):
    section = quality_tests
    verbose_name = 'Guideline Adherence Adult 2L Ratio'
    name = 'Guideline_Adherence_Adult_2L_Ratio'
    default = 0.80


@global_preferences_registry.register
class GuidelineAdherenceCheckAdult1LRatio(FloatPreference):
    section = quality_tests
    verbose_name = 'Guideline Adherence Adult 1L Ratio'
    name = 'Guideline_Adherence_Adult_1L_Ratio'
    default = 0.90
