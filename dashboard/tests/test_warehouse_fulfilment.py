from arrow import now
from django.test import TestCase
from mock import patch, call
from model_mommy import mommy

from dashboard.checks.warehouse_fulfilement import WarehouseFulfilment
from dashboard.helpers import YES, F1, F2, F3
from dashboard.models import Cycle, Consumption, Score
from locations.models import Facility


class TestWareHouseFulfilmentBalance(TestCase):
    @patch("dashboard.checks.warehouse_fulfilement.WarehouseFulfilment.record_result_for_facility")
    def test_should_record_result_for_facility(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [WarehouseFulfilment.F1_QUERY, WarehouseFulfilment.F2_QUERY, WarehouseFulfilment.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, packs_ordered=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, quantity_received=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        WarehouseFulfilment().run(current_cycle)
        calls = [call(current_record, YES, F1), call(current_record, YES, F2), call(current_record, YES, F3)]
        mock_method.assert_has_calls(calls)

    def test_should_calculate_correct_result(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [WarehouseFulfilment.F1_QUERY, WarehouseFulfilment.F2_QUERY, WarehouseFulfilment.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, packs_ordered=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, quantity_received=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        WarehouseFulfilment().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].warehouseFulfilment, "YES")
        self.assertEqual(Score.objects.all()[2].warehouseFulfilment, "YES")
        self.assertEqual(Score.objects.all()[0].warehouseFulfilment, "YES")

    @patch("dashboard.checks.warehouse_fulfilement.WarehouseFulfilment.build_cycle_formulation_score")
    def test_should_record_result_for_cycle(self, mock_method):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [WarehouseFulfilment.F1_QUERY, WarehouseFulfilment.F2_QUERY, WarehouseFulfilment.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, packs_ordered=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, quantity_received=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        WarehouseFulfilment().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        calls = [call(current_cycle, F1, 1, 0, 0, 1), call(current_cycle, F2, 1, 0, 0, 1), call(current_cycle, F3, 1, 0, 0, 1)]
        mock_method.assert_has_calls(calls)

    def test_should_handle_scenario_where_next_cycle_is_absent(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [WarehouseFulfilment.F1_QUERY, WarehouseFulfilment.F2_QUERY, WarehouseFulfilment.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, quantity_received=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        WarehouseFulfilment().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].warehouseFulfilment, "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[2].warehouseFulfilment, "NOT_REPORTING")
        self.assertEqual(Score.objects.all()[0].warehouseFulfilment, "NOT_REPORTING")

    def test_should_can_get_no(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [WarehouseFulfilment.F1_QUERY, WarehouseFulfilment.F2_QUERY, WarehouseFulfilment.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, packs_ordered=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, quantity_received=10, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        WarehouseFulfilment().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].warehouseFulfilment, "NO")
        self.assertEqual(Score.objects.all()[2].warehouseFulfilment, "NO")
        self.assertEqual(Score.objects.all()[0].warehouseFulfilment, "NO")

    def test_should_can_handle_blanks(self):
        prev_cycle = "Jan - Feb %s" % now().format("YYYY")
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        prev_record = mommy.make(Cycle, facility=facility, cycle=prev_cycle)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [WarehouseFulfilment.F1_QUERY, WarehouseFulfilment.F2_QUERY, WarehouseFulfilment.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=prev_record, packs_ordered=120, formulation=form)
            mommy.make(Consumption, facility_cycle=current_record, quantity_received=None, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        WarehouseFulfilment().run(current_cycle)
        self.assertEqual(Score.objects.count(), 3)
        self.assertEqual(Score.objects.all()[1].warehouseFulfilment, "NO")
        self.assertEqual(Score.objects.all()[2].warehouseFulfilment, "NO")
        self.assertEqual(Score.objects.all()[0].warehouseFulfilment, "NO")
