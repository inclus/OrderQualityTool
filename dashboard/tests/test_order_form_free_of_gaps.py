import json

from django.core.urlresolvers import reverse
from django_webtest import WebTest
from mock import MagicMock, patch

from dashboard.helpers import *
from dashboard.views.api import OrderFormFreeOfNegativeNumbersView, DifferentOrdersOverTimeView, ClosingBalanceView, \
    ConsumptionAndPatientsView, StableConsumptionView, WarehouseFulfilmentView, StablePatientVolumesView, \
    GuideLineAdherenceView


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

    @patch("dashboard.views.api.CycleFormulationScore.objects.filter")
    @patch("dashboard.views.api.now")
    def test_filter_is_setup(self, time_mock, filter_mock):
        time_mock.return_value = arrow.Arrow(2015, 12, 01)
        year = "2015"
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
        filter_mock.assert_called_with(
            cycle__in=[(u'Mar - Apr %s' % year), (u'May - Jun %s' % year), (u'Jul - Aug %s' % year),
                       (u'Sep - Oct %s' % year), (u'Nov - Dec %s' % year)], combination__icontains=u'reg',
            test=self.test)


class OrderFormFreeOfGapsViewTestCase(WebTest, RegimenCheckViewCaseMixin):
    url_name = 'order_form_free_of_gaps'
    test = ORDER_FORM_FREE_OF_GAPS

    def test_url_setup(self):
        url = reverse(self.url_name)
        response = self.app.get(url, user="testuser")
        self.assertEqual(200, response.status_code)

    @patch("dashboard.views.api.CycleFormulationScore.objects.filter")
    @patch("dashboard.views.api.now")
    def test_filter_is_setup(self, time_mock, filter_mock):
        time_mock.return_value = arrow.Arrow(2015, 12, 01)
        year = "2015"
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
        filter_mock.assert_called_with(
            cycle__in=[(u'Mar - Apr %s' % year), (u'May - Jun %s' % year), (u'Jul - Aug %s' % year),
                       (u'Sep - Oct %s' % year), (u'Nov - Dec %s' % year)], test=self.test)


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
