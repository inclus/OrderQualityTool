import json

from django.core.urlresolvers import reverse
from django_webtest import WebTest
from mock import MagicMock, patch

from dashboard.checks.order_form_free_of_gaps import OrderFormFreeOfGaps
from dashboard.helpers import *
from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord
from dashboard.views import *
from locations.models import Facility


class RegimenCheckViewCaseMixin():
    def get_url(self, end, start, url):
        return "%s?start=%s&&end=%s" % (url, start, end)


class OrderFormFreeOfNegativesViewTestCase(WebTest, RegimenCheckViewCaseMixin):
    url_name = 'order_form_free_of_negative_numbers'
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS
    view = OrderFormFreeOfNegativeNumbersView

    def test_view_is_wired_up(self):
        self.assertEqual(self.test, self.view.test)

    def get_url(self, end, start, url):
        regimen = "reg"
        return "%s?start=%s&&end=%s&&regimen=%s" % (url, start, end, regimen)

    @patch("dashboard.views.CycleFormulationTestScore.objects.filter")
    def test_filter_is_setup(self, filter_mock):
        today = arrow.now()
        year = today.format("YYYY")
        url = reverse(self.url_name)
        start = "Mar - Apr %s" % year
        end = "Nov - Dec %s" % year
        score = MagicMock()
        score.cycle = 'Mar - Apr %s' % year
        score.yes = 20
        score.no = 40
        score.not_reporting = 60
        filter_mock.return_value = [score]
        response = self.app.get(self.get_url(end, start, url), user="testuser")
        self.assertEqual(200, response.status_code)
        json_content = response.content.decode('utf8')
        data = json.loads(json_content)
        print(data)
        self.assertEqual(data['values'][0], {u'cycle': u'Mar - Apr 2015', u'no': 40, u'not_reporting': 60, u'yes': 20})
        filter_mock.assert_called_with(cycle__in=[(u'Mar - Apr %s' % year), (u'May - Jun %s' % year), (u'Jul - Aug %s' % year), (u'Sep - Oct %s' % year), (u'Nov - Dec %s' % year)], formulation__icontains=u'reg', test=self.test)


class OrderFormFreeOfGapsViewTestCase(WebTest, RegimenCheckViewCaseMixin):
    url_name = 'order_form_free_of_gaps'
    test = ORDER_FORM_FREE_OF_GAPS

    def test_url_setup(self):
        url = reverse(self.url_name)
        response = self.app.get(url, user="testuser")
        self.assertEqual(200, response.status_code)

    @patch("dashboard.views.CycleTestScore.objects.filter")
    def test_filter_is_setup(self, filter_mock):
        today = arrow.now()
        year = today.format("YYYY")
        url = reverse(self.url_name)
        start = "Mar - Apr %s" % year
        end = "Nov - Dec %s" % year
        score = MagicMock()
        score.cycle = 'Mar - Apr %s' % year
        score.yes = 20
        score.no = 40
        score.not_reporting = 60
        filter_mock.return_value = [score]
        response = self.app.get(self.get_url(end, start, url), user="testuser")
        self.assertEqual(200, response.status_code)
        json_content = response.content.decode('utf8')
        data = json.loads(json_content)
        self.assertEqual(data['values'][0], {u'cycle': u'Mar - Apr 2015', u'no': 40, u'not_reporting': 60, u'yes': 20})
        filter_mock.assert_called_with(cycle__in=[(u'Mar - Apr %s' % year), (u'May - Jun %s' % year), (u'Jul - Aug %s' % year), (u'Sep - Oct %s' % year), (u'Nov - Dec %s' % year)], test=self.test)

    def test_logic(self):
        names = ["FA1", "FA2", "FA3"]
        names_without_data = ["FA4", "FA5"]
        consumption_regimens = ["CREG-%s" % n for n in range(1, 26)]
        adult_regimens = ["AREG-%s" % n for n in range(1, 23)]
        paed_regimens = ["PREG-%s" % n for n in range(1, 9)]
        cycle = "Jan - Feb 2013"
        consumption_data = {}
        consumption_data['opening_balance'] = 3
        consumption_data['quantity_received'] = 4.5
        consumption_data['pmtct_consumption'] = 4.5
        consumption_data['art_consumption'] = 4.5
        consumption_data['loses_adjustments'] = 4.5
        consumption_data['closing_balance'] = 4.5
        consumption_data['months_of_stock_of_hand'] = 4
        consumption_data['quantity_required_for_current_patients'] = 4.5
        consumption_data['estimated_number_of_new_patients'] = 4.5
        consumption_data['estimated_number_of_new_pregnant_women'] = 4.5
        consumption_data['total_quantity_to_be_ordered'] = 4.5
        consumption_data['notes'] = None
        for name in names:
            facility, _ = Facility.objects.get_or_create(name=name)
            record, _ = FacilityCycleRecord.objects.get_or_create(cycle=cycle, facility=facility)
            consumption_data['facility_cycle'] = record
            for reg in consumption_regimens:
                consumption_data['formulation'] = reg
                FacilityConsumptionRecord.objects.create(**consumption_data)
            for reg in adult_regimens:
                AdultPatientsRecord.objects.create(facility_cycle=record, formulation=reg, existing=1.4, new=10.0)
            for reg in paed_regimens:
                PAEDPatientsRecord.objects.create(facility_cycle=record, formulation=reg, existing=3, new=12.0)

        for name in names_without_data:
            facility, _ = Facility.objects.get_or_create(name=name)
            record, _ = FacilityCycleRecord.objects.get_or_create(cycle=cycle, facility=facility)

        score = OrderFormFreeOfGaps().run(cycle)
        self.assertEqual(cycle, score.cycle)
        self.assertEqual(60.0, score.yes)
        self.assertEqual(0.0, score.no)
        self.assertEqual(40.0, score.not_reporting)


class DifferentOrdersOverTimeViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'different_orders_over_time'
    test = DIFFERENT_ORDERS_OVER_TIME
    view = DifferentOrdersOverTimeView


class ClosingBalanceViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'closing_balance_matches_opening_balance'
    test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE
    view = ClosingBalanceView


class ConsumptionAndPatientsViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'consumption_and_patients'
    test = CONSUMPTION_AND_PATIENTS
    view = ConsumptionAndPatientsView


class StableConsumptionViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'stable_consumption'
    test = STABLE_CONSUMPTION
    view = StableConsumptionView


class WarehouseFulfilmentViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'warehouse_fulfilment'
    test = WAREHOUSE_FULFILMENT
    view = WarehouseFulfilmentView


class StablePatientVolumesViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'stable_patient_volumes'
    test = STABLE_PATIENT_VOLUMES
    view = StablePatientVolumesView


class GuideLineAdherenceViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    url_name = 'guideline_adherence'
    test = GUIDELINE_ADHERENCE
    view = GuideLineAdherenceView
