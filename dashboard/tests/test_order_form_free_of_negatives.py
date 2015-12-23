from django_webtest import WebTest
from model_mommy import mommy

from dashboard.checks.order_free_of_negative_numbers import OrderFormFreeOfNegativeNumbers
from dashboard.helpers import *
from dashboard.models import Cycle, Consumption, Score, CycleFormulationScore
from dashboard.tests.test_order_form_free_of_gaps import RegimenCheckViewCaseMixin
from locations.models import Facility


class OrderFormFreeOfNegativesTestCase(WebTest, RegimenCheckViewCaseMixin):
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS

    def test_save_score_for_facility(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [OrderFormFreeOfNegativeNumbers.F1_QUERY, OrderFormFreeOfNegativeNumbers.F2_QUERY, OrderFormFreeOfNegativeNumbers.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(Score.objects.count(), 0)
        OrderFormFreeOfNegativeNumbers().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual([score['name'] for score in (Score.objects.values('name').distinct())], [facility.name])

    def test_save_score_for_cycle(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [OrderFormFreeOfNegativeNumbers.F1_QUERY, OrderFormFreeOfNegativeNumbers.F2_QUERY, OrderFormFreeOfNegativeNumbers.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, opening_balance=120, formulation=form)
        self.assertEqual(CycleFormulationScore.objects.count(), 0)
        OrderFormFreeOfNegativeNumbers().run(current_cycle)
        self.assertEqual(CycleFormulationScore.objects.count(), 3)
        self.assertEqual([score['test'] for score in (CycleFormulationScore.objects.values('test').distinct())], [self.test])

    def test_passes_if_no_negatives(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [OrderFormFreeOfNegativeNumbers.F1_QUERY, OrderFormFreeOfNegativeNumbers.F2_QUERY, OrderFormFreeOfNegativeNumbers.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, formulation=form, opening_balance=10, quantity_received=10, pmtct_consumption=10, art_consumption=10, estimated_number_of_new_pregnant_women=10, total_quantity_to_be_ordered=10)

        self.assertEqual(Score.objects.count(), 0)
        OrderFormFreeOfNegativeNumbers().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F1], YES)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F2], YES)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F3], YES)
    def test_fails_if_some_negatives(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [OrderFormFreeOfNegativeNumbers.F1_QUERY, OrderFormFreeOfNegativeNumbers.F2_QUERY, OrderFormFreeOfNegativeNumbers.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, formulation=form, opening_balance=-10, quantity_received=10, pmtct_consumption=10, art_consumption=10, estimated_number_of_new_pregnant_women=10, total_quantity_to_be_ordered=10)
        self.assertEqual(Score.objects.count(), 0)
        OrderFormFreeOfNegativeNumbers().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F1], NO)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F2], NO)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F3], NO)

    def test_not_reporting_if_formulations_not_found(self):
        current_cycle = "Mar - Apr %s" % now().format("YYYY")
        facility = mommy.make(Facility)
        current_record = mommy.make(Cycle, facility=facility, cycle=current_cycle)
        formulations = [OrderFormFreeOfNegativeNumbers.F1_QUERY, OrderFormFreeOfNegativeNumbers.F2_QUERY, OrderFormFreeOfNegativeNumbers.F3_QUERY]
        for form in formulations:
            mommy.make(Consumption, facility_cycle=current_record, formulation="YES FORM", opening_balance=-10, quantity_received=10, pmtct_consumption=10, art_consumption=10, estimated_number_of_new_pregnant_women=10, total_quantity_to_be_ordered=10)
        self.assertEqual(Score.objects.count(), 0)
        OrderFormFreeOfNegativeNumbers().run(current_cycle)
        self.assertEqual(Score.objects.count(), 1)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F1], NOT_REPORTING)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F2], NOT_REPORTING)
        self.assertEqual(Score.objects.all()[0].orderFormFreeOfNegativeNumbers[F3], NOT_REPORTING)
