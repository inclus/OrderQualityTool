from arrow import now
from django.test import TestCase
from model_mommy import mommy

from dashboard.checks.consumption_and_patients import ConsumptionAndPatients, CONSUMPTION_QUERY, MODEL, PATIENT_QUERY
from dashboard.helpers import YES, NOT_REPORTING, F1, F2, F3, NO
from dashboard.models import Cycle, Consumption, Score
from locations.models import Facility


class ConsumptionAndPatientsCheckTestCase(TestCase):
    def setUp(self):
        self.cycle = "Jan - Feb %s" % now().format("YYYY")
        self.check = ConsumptionAndPatients()

    def test_should_record_score_for_each_facility(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle)
        for form in self.check.formulations:
            mommy.make(Consumption, facility_cycle=current_record, pmtct_consumption=1, art_consumption=16, formulation=form[CONSUMPTION_QUERY])
            mommy.make(form[MODEL], facility_cycle=current_record, existing=5, new=5, formulation=form[PATIENT_QUERY])
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].consumptionAndPatients, {F1: YES, F2: NO, F3: NO})

    def test_should_record_pass_score_if_both_sums_of_df1_and_df2_zero(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle)
        for form in self.check.formulations:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=0, formulation=form[CONSUMPTION_QUERY])
            mommy.make(form[MODEL], facility_cycle=current_record, existing=0, new=0, formulation=form[PATIENT_QUERY])
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].consumptionAndPatients, {F1: YES, F2: YES, F3: YES})

    def test_should_record_no_score_if_one_sums_of_df1_and_df2_zero(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle)
        for form in self.check.formulations:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=0, formulation=form[CONSUMPTION_QUERY])
            mommy.make(form[MODEL], facility_cycle=current_record, existing=5, new=5, formulation=form[PATIENT_QUERY])
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].consumptionAndPatients, {F1: u'NO', F2: u'NO', F3: u'NO'})

    def test_should_record_pass_score_if_df1_is_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle)
        for form in self.check.formulations:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=None, formulation=form[CONSUMPTION_QUERY])
            mommy.make(form[MODEL], facility_cycle=current_record, existing=4, new=6, formulation=form[PATIENT_QUERY])
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].consumptionAndPatients, {F1: u'NO', F2: u'NO', F3: u'NO'})

    def test_should_record_pass_score_if_df2_is_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle)
        for form in self.check.formulations:
            mommy.make(Consumption, facility_cycle=current_record, pmtct_consumption=12, art_consumption=12, formulation=form[CONSUMPTION_QUERY])
            mommy.make(form[MODEL], facility_cycle=current_record, existing=None, new=None, formulation=form[PATIENT_QUERY])
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].consumptionAndPatients, {F1: u'NO', F2: u'NO', F3: u'NO'})

    def test_should_record_not_reporting_if_df1_has_no_records(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle)
        for form in self.check.formulations:
            mommy.make(Consumption, facility_cycle=current_record, art_consumption=12, formulation="dummy")
            mommy.make(form[MODEL], facility_cycle=current_record, existing=None, new=None, formulation=form[PATIENT_QUERY])
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].consumptionAndPatients, {F1: NOT_REPORTING, F2: NOT_REPORTING, F3: NOT_REPORTING})
