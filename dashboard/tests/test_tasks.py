from unittest import TestCase

from arrow import now
from mock import patch, MagicMock

from dashboard.tasks import calculate_scores_for_checks_in_cycle, import_general_report


class TaskTestCase(TestCase):
    @patch("dashboard.tasks.process_test")
    def x_test_calculate_scores_for_checks_in_cycle(self, mock_method):
        cycle = "Jan - Feb %s" % now().format("YYYY")
        calls = []
        calculate_scores_for_checks_in_cycle(cycle)
        mock_method.assert_has_calls(calls)

    def x_test_should_call_run_on_each_task(self):
        with self.assertRaises(NotImplementedError):
            cycle = "Jan - Feb %s" % now().format("YYYY")
            # process_test(Check, cycle)

    @patch("dashboard.tasks.calculate_scores_for_checks_in_cycle.delay")
    @patch("dashboard.tasks.GeneralReport")
    @patch("dashboard.tasks.os.remove")
    def x_test_import_general_report(self, mock_remove, mock_report, mock_calculate):
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
