import operator

from arrow import now
from django.db.models import F, Q
from django.test import TestCase
from model_mommy import mommy

from dashboard.checks.guideline_adherence import GuidelineAdherence, DF1, DF2, NAME, ADULT_1L, ADULT_2L, PAED_1L, FIELDS
from dashboard.helpers import YES, NO, NOT_REPORTING
from dashboard.models import Cycle, Consumption, Score, CycleFormulationScore
from locations.models import Facility


def get_df1_fields(total, v):
    total.extend(v[DF1])
    return total


def get_df2_fields(total, v):
    total.extend(v[DF2])
    return total


class GuidelineAdherenceAdult1LTestCase(TestCase):
    def setUp(self):
        self.cycle = "Jan - Feb %s" % now().format("YYYY")
        self.check = GuidelineAdherence()

    def test_should_record_score_for_each_facility(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == ADULT_1L, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=1, estimated_number_of_new_pregnant_women=1, formulation=form)
        self.assertEqual(0, Score.objects.all().count())
        self.check.run(self.cycle)
        self.assertEqual(1, Score.objects.all().count())
        self.assertEqual({'DEFAULT': YES}, Score.objects.all()[0].guidelineAdherenceAdult1L)

    def test_should_result_is_no_if_both_df2_fields_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == ADULT_1L, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=None, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherenceAdult1L, {'DEFAULT': NO})

    def test_should_result_is_no_if_both_df1_fields_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == ADULT_1L, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=None, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=12, estimated_number_of_new_pregnant_women=23, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherenceAdult1L, {'DEFAULT': NO})

    def test_can_handle_blanks(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == ADULT_1L, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=19, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=2, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherenceAdult1L, {'DEFAULT': YES})

    def test_should_record_score_for_each_cycle(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == ADULT_1L, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=1, estimated_number_of_new_pregnant_women=1, formulation=form)
        self.assertEqual(0, CycleFormulationScore.objects.all().count())
        self.check.run(self.cycle)
        self.assertEqual(3, CycleFormulationScore.objects.all().count())
        self.assertEqual(self.cycle, CycleFormulationScore.objects.all()[0].cycle)
        self.assertEqual(100.0, CycleFormulationScore.objects.all()[0].yes)

    def test_score_is_yes_if_sum_of_new_hiv_positive_women_and_new_art_for_tdf_is_80_percent_that_for_AZT(self):
        check = GuidelineAdherence()
        df1_count = df2_count = 1
        sum_df1 = 9
        sum_df2 = 2
        ratio = 0.8
        no, not_reporting, result, yes = check.calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, 0, 0, 0)
        self.assertEqual(result, YES)
        self.assertEqual(yes, 1)
        self.assertEqual(no, 0)
        self.assertEqual(not_reporting, 0)

    def test_score_is_yes_if_sum_of_new_hiv_positive_women_and_new_art_for_tdf_is_zero_and_that_for_AZT_is_also_zero(self):
        check = GuidelineAdherence()
        df1_count = df2_count = 1
        sum_df1 = 0
        sum_df2 = 0
        ratio = 0.8
        no, not_reporting, result, yes = check.calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, 0, 0, 0)
        self.assertEqual(result, YES)
        self.assertEqual(yes, 1)
        self.assertEqual(no, 0)
        self.assertEqual(not_reporting, 0)

    def test_score_is_no_if_tdf_cells_are_blank(self):
        check = GuidelineAdherence()
        df1_count = df2_count = 1
        sum_df1 = 0
        sum_df2 = 12
        ratio = 0.8
        no, not_reporting, result, yes = check.calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, 0, 0, 0, True, False)
        self.assertEqual(result, NO)
        self.assertEqual(yes, 0)
        self.assertEqual(no, 1)
        self.assertEqual(not_reporting, 0)

    def test_score_is_no_if_azt_cells_are_blank(self):
        check = GuidelineAdherence()
        df1_count = df2_count = 1
        sum_df1 = 0
        sum_df2 = 0
        ratio = 0.8
        no, not_reporting, result, yes = check.calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, 0, 0, 0, False, True)
        self.assertEqual(result, NO)
        self.assertEqual(yes, 0)
        self.assertEqual(no, 1)
        self.assertEqual(not_reporting, 0)

    def test_score_is_not_reporting_if_azt_or_tdf_cells_are_not_found(self):
        check = GuidelineAdherence()
        df1_count = df2_count = 0
        sum_df1 = 0
        sum_df2 = 0
        ratio = 0.8
        no, not_reporting, result, yes = check.calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, 0, 0, 0, False, True)
        self.assertEqual(result, NOT_REPORTING)
        self.assertEqual(yes, 0)
        self.assertEqual(no, 0)
        self.assertEqual(not_reporting, 1)

    def test_can_get_correct_sum(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        formulation = self.check.formulations[0]
        df1_sum_fields = reduce(operator.add, (F(item) for item in formulation[FIELDS]))
        df1_filter = reduce(operator.or_, (Q(formulation__icontains=item) for item in formulation[DF1]))
        df1_qs = Consumption.objects.filter(facility_cycle=current_record).filter(df1_filter)
        sum = self.check.get_sum(df1_qs, df1_sum_fields)
        self.assertEqual(sum, 0)


class GuidelineAdherenceAdult2LTestCase(TestCase):
    guideline = ADULT_2L

    def setUp(self):
        self.cycle = "Jan - Feb %s" % now().format("YYYY")
        self.check = GuidelineAdherence()

    def test_should_record_score_for_each_facility(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=1, estimated_number_of_new_pregnant_women=1, formulation=form)
        self.assertEqual(0, Score.objects.all().count())
        self.check.run(self.cycle)
        self.assertEqual(1, Score.objects.all().count())
        self.assertEqual({'DEFAULT': YES}, Score.objects.all()[0].guidelineAdherenceAdult2L)

    def test_should_result_is_no_if_both_df2_fields_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=None, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherenceAdult2L, {'DEFAULT': NO})

    def test_should_result_is_no_if_both_df1_fields_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=None, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=12, estimated_number_of_new_pregnant_women=23, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherenceAdult2L, {'DEFAULT': NO})

    def test_can_handle_blanks(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=19, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=3, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherenceAdult2L, {'DEFAULT': YES})

    def test_should_record_score_for_each_cycle(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=1, estimated_number_of_new_pregnant_women=1, formulation=form)
        self.assertEqual(0, CycleFormulationScore.objects.all().count())
        self.check.run(self.cycle)
        self.assertEqual(3, CycleFormulationScore.objects.all().count())
        self.assertEqual(self.cycle, CycleFormulationScore.objects.all()[0].cycle)
        self.assertEqual(100.0, CycleFormulationScore.objects.all()[1].yes)


class GuidelineAdherencePaed1LTestCase(TestCase):
    guideline = PAED_1L

    def setUp(self):
        self.cycle = "Jan - Feb %s" % now().format("YYYY")
        self.check = GuidelineAdherence()

    def test_should_record_score_for_each_facility(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=8, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=1, estimated_number_of_new_pregnant_women=1, formulation=form)
        self.assertEqual(0, Score.objects.all().count())
        self.check.run(self.cycle)
        self.assertEqual(1, Score.objects.all().count())
        self.assertEqual({'DEFAULT': YES}, Score.objects.all()[0].guidelineAdherencePaed1L)

    def test_should_result_is_no_if_both_df2_fields_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=4, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=None, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherencePaed1L, {'DEFAULT': NO})

    def test_should_result_is_no_if_both_df1_fields_null(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=None, estimated_number_of_new_pregnant_women=None, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=12, estimated_number_of_new_pregnant_women=23, formulation=form)
        self.assertEqual(Score.objects.all().count(), 0)
        self.check.run(self.cycle)
        self.assertEqual(Score.objects.all().count(), 1)
        self.assertEqual(Score.objects.all()[0].guidelineAdherencePaed1L, {'DEFAULT': NO})

    def test_should_record_score_for_each_cycle(self):
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=self.cycle, reporting_status=True)
        adult_formulations = filter(lambda x: x[NAME] == self.guideline, GuidelineAdherence.formulations)
        df1_formulations = reduce(get_df1_fields, adult_formulations, [])
        df2_formulations = reduce(get_df2_fields, adult_formulations, [])

        for form in df1_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=8, estimated_number_of_new_pregnant_women=4, formulation=form)

        for form in df2_formulations:
            mommy.make(Consumption, facility_cycle=current_record, estimated_number_of_new_patients=1, estimated_number_of_new_pregnant_women=1, formulation=form)
        self.assertEqual(0, CycleFormulationScore.objects.all().count())
        self.check.run(self.cycle)
        self.assertEqual(3, CycleFormulationScore.objects.all().count())
        self.assertEqual(self.cycle, CycleFormulationScore.objects.all()[0].cycle)
        self.assertEqual(100.0, CycleFormulationScore.objects.all()[2].yes)
