from unittest import TestCase

from arrow import now
from mock import patch, call, MagicMock

from dashboard.checks.closing_balance import ClosingBalance
from dashboard.checks.common import Check
from dashboard.checks.consumption_and_patients import ConsumptionAndPatients
from dashboard.checks.different_orders_over_time import DifferentOrdersOverTime
from dashboard.checks.guideline_adherence import GuidelineAdherence
from dashboard.checks.nnrti_checks import NNRTI
from dashboard.checks.order_form_free_of_gaps import OrderFormFreeOfGaps
from dashboard.checks.order_free_of_negative_numbers import OrderFormFreeOfNegativeNumbers
from dashboard.checks.stable_consumption import StableConsumption
from dashboard.checks.stable_patient_volumes import StablePatientVolumes
from dashboard.checks.warehouse_fulfilement import WarehouseFulfilment
from dashboard.checks.web_based_reporting import WebBasedReportingCheck, ReportingCheck, MultipleOrdersCheck
from dashboard.tasks import calculate_scores_for_checks_in_cycle, process_test, import_general_report


class TaskTestCase(TestCase):
    @patch("dashboard.tasks.process_test")
    def test_calculate_scores_for_checks_in_cycle(self, mock_method):
        cycle = "Jan - Feb %s" % now().format("YYYY")
        calls = [
            call(WebBasedReportingCheck, cycle),
            call(ReportingCheck, cycle),
            call(MultipleOrdersCheck, cycle),
            call(OrderFormFreeOfGaps, cycle),
            call(OrderFormFreeOfNegativeNumbers, cycle),
            call(DifferentOrdersOverTime, cycle),
            call(ClosingBalance, cycle),
            call(ConsumptionAndPatients, cycle),
            call(StableConsumption, cycle),
            call(WarehouseFulfilment, cycle),
            call(StablePatientVolumes, cycle),
            call(GuidelineAdherence, cycle),
            call(NNRTI, cycle)]
        calculate_scores_for_checks_in_cycle(cycle)
        mock_method.assert_has_calls(calls)

    def test_should_call_run_on_each_task(self):
        with self.assertRaises(NotImplementedError):
            cycle = "Jan - Feb %s" % now().format("YYYY")
            process_test(Check, cycle)

    @patch("dashboard.tasks.calculate_scores_for_checks_in_cycle.delay")
    @patch("dashboard.tasks.GeneralReport")
    @patch("dashboard.tasks.os.remove")
    def test_import_general_report(self, mock_remove, mock_report, mock_calculate):
        mock_report_instance = MagicMock()
        mock_report_instance.get_data = MagicMock()
        mock_report.return_value = mock_report_instance
        cycle = "Jan - Feb %s" % now().format("YYYY")
        path = "path"
        import_general_report(path, cycle)
        mock_remove.assert_called_with(path)
        mock_report.assert_called_with(path, cycle)
        mock_report_instance.get_data.assert_called_with()
        mock_calculate.assert_called_with(cycle)
