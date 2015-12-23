from arrow import now
from django.test import TestCase
from mock import patch, call
from model_mommy import mommy

from dashboard.checks.closing_balance import ClosingBalance
from dashboard.helpers import YES, F1, F2, F3, NO
from dashboard.models import Cycle, Consumption, Score
from locations.models import Facility


class TestClosingBalance(TestCase):
    @patch("dashboard.checks.closing_balance.ClosingBalance.record_result_for_facility")
    def test_should_record_result_for_facility(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [ClosingBalance.F1_QUERY, ClosingBalance.F2_QUERY, ClosingBalance.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, closing_balance=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        ClosingBalance().run(current_cycle)
        calls = [call(current_record, YES, F1), call(current_record, YES, F2), call(current_record, YES, F3)]
        mock_method.assert_has_calls(calls)

    def test_should_calculate_correct_result(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [ClosingBalance.F1_QUERY, ClosingBalance.F2_QUERY, ClosingBalance.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, closing_balance=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        ClosingBalance().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F1], "YES")
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F2], "YES")
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F3], "YES")


    @patch("dashboard.checks.closing_balance.ClosingBalance.build_cycle_formulation_score")
    def test_should_record_result_for_cycle(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [ClosingBalance.F1_QUERY, ClosingBalance.F2_QUERY, ClosingBalance.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, closing_balance=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        ClosingBalance().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        calls = [call(current_cycle, F1, 1, 0, 0, 1), call(current_cycle, F2, 1, 0, 0, 1), call(current_cycle, F3, 1, 0, 0, 1)]
        mock_method.assert_has_calls(calls)

    def test_should_handle_scenario_where_next_cycle_is_absent(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [ClosingBalance.F1_QUERY, ClosingBalance.F2_QUERY, ClosingBalance.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        ClosingBalance().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F1], "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F2], "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F3], "NOT_REPORTING")

    def test_should_query_correct_formulation(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [ClosingBalance.F1_QUERY, ClosingBalance.F2_QUERY, ClosingBalance.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, closing_balance=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=10, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        ClosingBalance().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F1], "NO")
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F2], "NO")
        self.assertEqual(Score.objects.all()[0].closingBalanceMatchesOpeningBalance[F3], "NO")

    def test_compare_values(self):
        check = ClosingBalance()
        cases = [{"closing": 1, "open": 1, "yes": 1, "no": 0, "result": YES}, {"closing": 1, "open": 2, "yes": 0, "no": 1, "result": NO}]
        for case in cases:
            no, result, yes = check.compare_values([{"opening_balance": case["open"]}], [{"closing_balance": case["closing"]}], 0, "", 0)
            self.assertEqual(yes, case["yes"])
            self.assertEqual(no, case["no"])
            self.assertEqual(result, case["result"])
