from django.test import TestCase

from dashboard.checks.comparisons import calculate_percentage_variance, PercentageVarianceLessThanComparison, \
    AtLeastNOfTotal, Comparison
from dashboard.checks.entities import GroupResult, DefinitionGroup, GroupModel, DefinitionOption, DataRecord
from dashboard.checks.tracer import Tracer


class TestPercentageVarianceLessThanComparison(TestCase):
    def test_differ_by_less_than_50(self):
        self.assertFalse(PercentageVarianceLessThanComparison().compare(100, 201, 50))
        self.assertFalse(PercentageVarianceLessThanComparison().compare(-11.5, None, 50))
        self.assertFalse(PercentageVarianceLessThanComparison().compare(201, 100, 50))
        self.assertTrue(PercentageVarianceLessThanComparison().compare(200, 100, 50))
        self.assertTrue(PercentageVarianceLessThanComparison().compare(30, 60, 50))

    def test_dont_differ_by_less_than_50(self):
        self.assertTrue(PercentageVarianceLessThanComparison().compare(10, 14, 50))
        self.assertAlmostEqual(calculate_percentage_variance(10, 14.0), 400.0 / 14)
        self.assertFalse(PercentageVarianceLessThanComparison().compare(0, 3, 50))
        self.assertEquals(calculate_percentage_variance(3, 0), 100)
        self.assertFalse(PercentageVarianceLessThanComparison().compare(3, 0, 50))
        self.assertTrue(PercentageVarianceLessThanComparison().compare(14, 9, 50))
        self.assertTrue(PercentageVarianceLessThanComparison().compare(10, 10, 50))


current_cycle = DefinitionOption(id='Current', name='Current Cycle')
previous_cycle = DefinitionOption(id='Previous', name='Previous Cycle')
sum_comparison = DefinitionOption(id='SUM', name='SUM')
r1 = DataRecord(
    formulation='Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]',
    values=[50.0], fields=['consumption'])
r2 = DataRecord(
    formulation='Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]',
    values=[0], fields=['consumption'])
tracer = Tracer(key=u'tdf3tcefv-adult',
                consumption_formulations=[u'Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]'],
                patient_formulations=[u'TDF/3TC/EFV (PMTCT)', u'TDF/3TC/EFV (ADULT)'], extras=None)


class TestThresholds(TestCase):
    def test_groups_have_insufficient_data_if_the_aggregate_is_below_the_threshold(self):
        group1 = DefinitionGroup(name='G1', model=None, cycle=current_cycle, selected_fields=['consumption'],
                                 selected_formulations=[], sample_formulation_model_overridden={},
                                 sample_formulation_model_overrides={}, aggregation=sum_comparison, has_factors=None,
                                 factors=None,
                                 has_thresholds=True,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 200})
        group2 = DefinitionGroup(name='G2', model=None, cycle=previous_cycle,
                                 selected_fields=['consumption'], selected_formulations=[],
                                 sample_formulation_model_overridden={}, sample_formulation_model_overrides={},
                                 aggregation=sum_comparison, has_factors=None, factors=None, has_thresholds=True,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 200})
        result1 = GroupResult(
            group=group1,
            values=None,
            factored_records=[r1],
            aggregate=50.0,
            tracer=tracer
        )

        result2 = GroupResult(
            group=group2,
            values=None,
            factored_records=[r2],
            aggregate=40.0,
            tracer=tracer)

        self.assertFalse(Comparison().groups_have_adequate_data([result1, result2]))

    def test_groups_have_sufficient_data_if_the_aggregate_is_above_the_threshold(self):
        group1 = DefinitionGroup(name='G1', model=None, cycle=current_cycle, selected_fields=['consumption'],
                                 selected_formulations=[], sample_formulation_model_overridden={},
                                 sample_formulation_model_overrides={}, aggregation=sum_comparison, has_factors=None,
                                 factors=None,
                                 has_thresholds=True,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 30})
        group2 = DefinitionGroup(name='G2', model=None, cycle=previous_cycle,
                                 selected_fields=['consumption'], selected_formulations=[],
                                 sample_formulation_model_overridden={}, sample_formulation_model_overrides={},
                                 aggregation=sum_comparison, has_factors=None, factors=None, has_thresholds=True,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 20})
        result1 = GroupResult(
            group=group1,
            values=None,
            factored_records=[r1],
            aggregate=50.0,
            tracer=tracer
        )

        result2 = GroupResult(
            group=group2,
            values=None,
            factored_records=[r2],
            aggregate=40.0,
            tracer=tracer)

        self.assertTrue(Comparison().groups_have_adequate_data([result1, result2]))


class TestAtLeastNOfTotalComparison(TestCase):
    def test_comparison(self):
        self.assertTrue(AtLeastNOfTotal().compare(200, 100, 50))
        self.assertFalse(AtLeastNOfTotal().compare(4183, None, 50))
        self.assertEqual(AtLeastNOfTotal().text(200, None, 50), "second value is zero so the check fails")
        self.assertEqual(AtLeastNOfTotal().text(200, 100, 50), "200 is more than 50% of 300")
        self.assertTrue(AtLeastNOfTotal().compare(10, 14, 10))
        self.assertTrue(AtLeastNOfTotal().compare(14, 9, 50))
        self.assertFalse(AtLeastNOfTotal().compare(10, 60, 50))
        self.assertEqual(AtLeastNOfTotal().text(10, 60, 50), "10 is less than 50% of 70")

    def test_groups_have_sufficient_data_if_the_aggregate_second_group_is_greater_than_zero(self):
        group1 = DefinitionGroup(name='G1', model=None, cycle=current_cycle, selected_fields=['consumption'],
                                 selected_formulations=[], sample_formulation_model_overridden={},
                                 sample_formulation_model_overrides={}, aggregation=sum_comparison, has_factors=None,
                                 factors=None,
                                 has_thresholds=False,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 30})
        group2 = DefinitionGroup(name='G2', model=None, cycle=previous_cycle,
                                 selected_fields=['consumption'], selected_formulations=[],
                                 sample_formulation_model_overridden={}, sample_formulation_model_overrides={},
                                 aggregation=sum_comparison, has_factors=None, factors=None, has_thresholds=False,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 20})
        result1 = GroupResult(
            group=group1,
            values=None,
            factored_records=[r1],
            aggregate=50.0,
            tracer=tracer
        )

        result2 = GroupResult(
            group=group2,
            values=None,
            factored_records=[r2],
            aggregate=40.0,
            tracer=tracer)

        self.assertTrue(AtLeastNOfTotal().groups_have_adequate_data([result1, result2]))

    def test_groups_have_insufficient_data_if_the_aggregate_second_group_is_zero(self):
        group1 = DefinitionGroup(name='G1', model=None, cycle=current_cycle, selected_fields=['consumption'],
                                 selected_formulations=[], sample_formulation_model_overridden={},
                                 sample_formulation_model_overrides={}, aggregation=sum_comparison, has_factors=None,
                                 factors=None,
                                 has_thresholds=True,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 20})
        group2 = DefinitionGroup(name='G2', model=None, cycle=previous_cycle,
                                 selected_fields=['consumption'], selected_formulations=[],
                                 sample_formulation_model_overridden={}, sample_formulation_model_overrides={},
                                 aggregation=sum_comparison, has_factors=None, factors=None, has_thresholds=True,
                                 thresholds={u'abc3tc-paed': 10, u'efv200-paed': 10, u'tdf3tcefv-adult': 20})
        result1 = GroupResult(
            group=group1,
            values=None,
            factored_records=[r1],
            aggregate=50.0,
            tracer=None
        )

        result2 = GroupResult(
            group=group2,
            values=None,
            factored_records=[r2],
            aggregate=0.0,
            tracer=None)

        self.assertFalse(AtLeastNOfTotal().groups_have_adequate_data([result1, result2]))
