from arrow import now
from django.test import TestCase
from mock import patch, call
from model_mommy import mommy

from dashboard.checks.different_orders_over_time import get_prev_cycle, DifferentOrdersOverTime
from dashboard.checks.stable_consumption import StableConsumption
from dashboard.helpers import DIFFERENT_ORDERS_OVER_TIME, NO, YES, F1, F2, F3
from dashboard.models import Cycle, Consumption, CycleFormulationScore, Score
from locations.models import Facility


class DifferentOrdersOverTimeTestCase(TestCase):
    def test_gen_next_cycle(self):
        values = [('Jan - Feb 2013', 'Mar - Apr 2013'), ('Nov - Dec 2013', 'Jan - Feb 2014'), ('Mar - Apr 2014', 'May - Jun 2014')]
        for v in values:
            self.assertEqual(get_prev_cycle(v[1]), v[0])

    @patch("dashboard.checks.different_orders_over_time.DifferentOrdersOverTime.record_result_for_facility")
    def test_should_record_result_for_facility(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [DifferentOrdersOverTime.F1_QUERY, DifferentOrdersOverTime.F2_QUERY, DifferentOrdersOverTime.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, opening_balance=13, estimated_number_of_new_patients=10, art_consumption=12, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, estimated_number_of_new_patients=10, art_consumption=12, formulation=form)
        self.assertEqual(Score.objects.count(), 0)

        DifferentOrdersOverTime().run(current_cycle)
        calls = [call(current_record, YES, F1), call(current_record, YES, F2), call(current_record, YES, F3)]
        mock_method.assert_has_calls(calls)

    def test_compare_values_when_same(self):
        check = DifferentOrdersOverTime()
        no, result, yes = check.compare_values([{'opening_balance': 10, 'art_consumption': 12, 'estimated_number_of_new_patients': 13}], [{'opening_balance': 10, 'art_consumption': 12, 'estimated_number_of_new_patients': 13}], 0, "", 0)
        self.assertEqual(yes, 0)
        self.assertEqual(no, 1)
        self.assertEqual(result, NO)

    def test_compare_values_when_one_same(self):
        check = DifferentOrdersOverTime()
        no, result, yes = check.compare_values([{'opening_balance': 10, 'art_consumption': 13, 'estimated_number_of_new_patients': 13}], [{'opening_balance': 10, 'art_consumption': 12, 'estimated_number_of_new_patients': 13}], 0, "", 0)
        self.assertEqual(yes, 1)
        self.assertEqual(no, 0)
        self.assertEqual(result, YES)

    def test_compare_values_when_one_same_with_blank(self):
        check = DifferentOrdersOverTime()
        no, result, yes = check.compare_values([{'opening_balance': 10, 'art_consumption': None, 'estimated_number_of_new_patients': 13}], [{'opening_balance': 10, 'art_consumption': 12, 'estimated_number_of_new_patients': 13}], 0, "", 0)
        self.assertEqual(yes, 1)
        self.assertEqual(no, 0)
        self.assertEqual(result, YES)

    def test_compare_values_when_one_same_when_all_zeros(self):
        check = DifferentOrdersOverTime()
        no, result, yes = check.compare_values([{'opening_balance': 0, 'art_consumption': 0, 'estimated_number_of_new_patients': 0}], [{'opening_balance': 0, 'art_consumption': 0, 'estimated_number_of_new_patients': 0}], 0, "", 0)
        self.assertEqual(yes, 1)
        self.assertEqual(no, 0)
        self.assertEqual(result, YES)

    def test_check(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [DifferentOrdersOverTime.F1_QUERY, DifferentOrdersOverTime.F2_QUERY, DifferentOrdersOverTime.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, opening_balance=13, estimated_number_of_new_patients=10, art_consumption=12, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, estimated_number_of_new_patients=10, art_consumption=12, formulation=form)
        self.assertEqual(Score.objects.count(), 0)

        DifferentOrdersOverTime().run(current_cycle)
        score = CycleFormulationScore.objects.filter(test=DIFFERENT_ORDERS_OVER_TIME, cycle=current_cycle)[0]
        self.assertEquals(score.yes, 100.0)
        self.assertEquals(score.no, 0.0)
        self.assertEquals(score.not_reporting, 0.0)

    def test_should_handle_scenario_where_next_cycle_is_absent(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [DifferentOrdersOverTime.F1_QUERY, DifferentOrdersOverTime.F2_QUERY, DifferentOrdersOverTime.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        DifferentOrdersOverTime().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].differentOrdersOverTime, "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[2].differentOrdersOverTime, "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[0].differentOrdersOverTime, "NOT_REPORTING")


class StableConsumptionTestCase(TestCase):
    @patch("dashboard.checks.stable_consumption.StableConsumption.record_result_for_facility")
    def test_should_record_result_for_facility(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, art_consumption=10, pmtct_consumption=30, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=10, pmtct_consumption=30, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        calls = [call(current_record, YES, F1), call(current_record, YES, F2), call(current_record, YES, F3)]
        mock_method.assert_has_calls(calls)

    def test_should_calculate_correct_result(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, art_consumption=10, pmtct_consumption=30, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=10, pmtct_consumption=30, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].stableConsumption, "YES")
        self.assertEqual(Score.objects.all()[2].stableConsumption, "YES")
        self.assertEqual(Score.objects.all()[0].stableConsumption, "YES")

    def test_can_get_no(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, art_consumption=200, pmtct_consumption=300, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=10, pmtct_consumption=30, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].stableConsumption, "NO")
        self.assertEqual(Score.objects.all()[2].stableConsumption, "NO")
        self.assertEqual(Score.objects.all()[0].stableConsumption, "NO")

    def test_should_only_consider_facilities_with_consumption_over_20(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, art_consumption=None, pmtct_consumption=30, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=5, pmtct_consumption=3, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        self.assertEqual(Score.objects.count(), 0)

    @patch("dashboard.checks.stable_consumption.StableConsumption.build_cycle_formulation_score")
    def test_should_record_result_for_cycle(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, art_consumption=10, pmtct_consumption=30, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=10, pmtct_consumption=30, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        calls = [call(current_cycle, F1, 1, 0, 0, 1), call(current_cycle, F2, 1, 0, 0, 1), call(current_cycle, F3, 1, 0, 0, 1)]
        mock_method.assert_has_calls(calls)

    def test_should_handle_scenario_where_next_cycle_is_absent(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=10, pmtct_consumption=30, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].stableConsumption, "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[2].stableConsumption, "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[0].stableConsumption, "NOT_REPORTING")

    def test_can_handle_blanks(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [StableConsumption.F1_QUERY, StableConsumption.F2_QUERY, StableConsumption.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, art_consumption=None, pmtct_consumption=None, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=40, pmtct_consumption=10, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        StableConsumption().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].stableConsumption, "NO")
        self.assertEqual(Score.objects.all()[2].stableConsumption, "NO")
        self.assertEqual(Score.objects.all()[0].stableConsumption, "NO")
