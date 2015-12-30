from arrow import now
from django.test import TestCase
from mock import patch, call
from model_mommy import mommy

from dashboard.checks.nnrti_checks import NNRTI
from dashboard.helpers import YES, NOT_REPORTING, NO, NNRTI_CURRENT_PAED, NNRTI_NEW_PAED, NNRTI_NEW_ADULTS
from dashboard.models import Cycle, Consumption, CycleScore
from locations.models import Facility


class NNRTITestCase(TestCase):
    def test_not_reporting_if_df1_count_is_zero(self):
        DF1_VALUE = 10
        DF2_VALUE = 10
        df1_count = 0
        df2_count = 4
        sum_df1 = df1_count * DF1_VALUE
        sum_df2 = df2_count * DF2_VALUE
        total = sum_df2 + sum_df1
        check = NNRTI()
        no, not_reporting, result, yes = check.compare_values(4.6, 0, 0, 0, df1_count, df2_count, sum_df1, sum_df2, total)
        self.assertEqual(result, NOT_REPORTING)
        self.assertEqual(yes, 0)
        self.assertEqual(no, 0)
        self.assertEqual(not_reporting, 1)

    def test_not_reporting_if_df2_count_is_zero(self):
        DF1_VALUE = 10
        DF2_VALUE = 10
        df1_count = 2
        df2_count = 0
        sum_df1 = df1_count * DF1_VALUE
        sum_df2 = df2_count * DF2_VALUE
        total = sum_df2 + sum_df1
        check = NNRTI()
        no, not_reporting, result, yes = check.compare_values(4.6, 0, 0, 0, df1_count, df2_count, sum_df1, sum_df2, total)
        self.assertEqual(result, NOT_REPORTING)
        self.assertEqual(yes, 0)
        self.assertEqual(no, 0)
        self.assertEqual(not_reporting, 1)

    def test_fails_if_total_is_zero(self):
        DF1_VALUE = 0
        DF2_VALUE = 0
        df1_count = 2
        df2_count = 2
        sum_df1 = df1_count * DF1_VALUE
        sum_df2 = df2_count * DF2_VALUE
        total = sum_df2 + sum_df1
        check = NNRTI()
        no, not_reporting, result, yes = check.compare_values(4.6, 0, 0, 0, df1_count, df2_count, sum_df1, sum_df2, total)
        self.assertEqual(result, YES)
        self.assertEqual(yes, 1)
        self.assertEqual(no, 0)
        self.assertEqual(not_reporting, 0)

    def test_can_pass(self):
        DF1_VALUE = 80
        DF2_VALUE = 10
        df1_count = 2
        df2_count = 4
        sum_df1 = df1_count * DF1_VALUE
        sum_df2 = df2_count * DF2_VALUE
        total = sum_df2 + sum_df1
        check = NNRTI()
        no, not_reporting, result, yes = check.compare_values(4.6, 0, 0, 0, df1_count, df2_count, sum_df1, sum_df2, total)
        self.assertEqual(result, YES)

    def test_can_fail(self):
        DF1_VALUE = 800
        DF2_VALUE = 10
        df1_count = 2
        df2_count = 4
        sum_df1 = df1_count * DF1_VALUE
        sum_df2 = df2_count * DF2_VALUE
        total = sum_df2 + sum_df1
        check = NNRTI()
        no, not_reporting, result, yes = check.compare_values(4.6, 0, 0, 0, df1_count, df2_count, sum_df1, sum_df2, total)
        self.assertEqual(result, NO)

    @patch("dashboard.checks.nnrti_checks.NNRTI.record_result_for_facility")
    @patch("dashboard.checks.nnrti_checks.NNRTI.compare_values")
    def test_check_records_results_for_facility(self, mock_method, mock_facility_method):
        mock_method.return_value = (0, 0, YES, 1)
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle, reporting_status=True)
        NNRTI().run(current_cycle)
        calls = [call(current_record, YES, test=NNRTI_CURRENT_PAED), call(current_record, YES, test=NNRTI_NEW_ADULTS), call(current_record, YES, test=NNRTI_NEW_PAED)]
        mock_facility_method.assert_has_calls(calls)

    @patch("dashboard.checks.nnrti_checks.NNRTI.compare_values")
    def test_check_records_results_for_cycle(self, mock_method):
        mock_method.return_value = (0, 0, YES, 1)
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle, reporting_status=True)
        NNRTI().run(current_cycle)
        self.assertEqual(CycleScore.objects.count(), 4)
        self.assertEqual(CycleScore.objects.all()[0].yes, 100.0)
        self.assertEqual(CycleScore.objects.all()[0].no, 0.0)
        self.assertEqual(CycleScore.objects.all()[0].not_reporting, 0.0)


class TestNNRTI_CURRENT_PAED(TestCase):
    @patch("dashboard.checks.nnrti_checks.NNRTI.compare_values")
    def test_check_queries_correct_data(self, mock_method):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle, reporting_status=True)
        DF2 = [
            "Efavirenz (EFV) 200mg [Pack 90]",
            "Nevirapine (NVP) 50mg [Pack 60]",
            "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
            "Lopinavir/Ritonavir (LPV/r) 100mg/25mg",
        ]
        DF1 = [
                  "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]",
                  "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
              ],
        DF1_VALUE = 10
        DF2_VALUE = 5
        for f in DF1:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=DF1_VALUE, formulation=f)
        for f in DF2:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=DF2_VALUE, formulation=f)
        mock_method.return_value = (0, 0, YES, 1)
        NNRTI().run(current_cycle)
        ratio = 4.6
        no = 0
        not_reporting = 0
        yes = 0
        df1_count = len(DF1)
        df2_count = len(DF2)
        sum_df1 = len(DF1) * DF1_VALUE
        sum_df2 = len(DF2) * DF2_VALUE
        total = sum_df2 + sum_df1
        expected_call = call(ratio, no, not_reporting, yes, df1_count, df2_count, sum_df1, sum_df2, total)
        mock_method.assert_has_calls([expected_call])
