import json

from arrow import utcnow
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from mock import patch

from dashboard.helpers import *
from dashboard.models import Score, FacilityTest


class OrderFormFreeOfNegativesViewTestCase(WebTest):
    url_name = "test_scores_api"
    test_id = 7
    formulation = F1

    def get_url(self, end, start, url):
        regimen = F1
        return "%s?start=%s&&end=%s&&regimen=%s" % (url, start, end, regimen)

    @patch("dashboard.views.api.now")
    def test_filter_is_setup(self, time_mock):
        time_mock.return_value = arrow.Arrow(2015, 12, 1)
        year = "2015"
        test = FacilityTest.objects.get(id=self.test_id).name
        url = reverse(self.url_name, kwargs={"id": self.test_id})
        start = "Mar - Apr %s" % year
        end = "Nov - Dec %s" % year
        Score.objects.create(
            data={test: {self.formulation: YES}}, name="F4", cycle=start
        )
        Score.objects.create(
            data={test: {self.formulation: NO}}, name="F5", cycle=start
        )
        Score.objects.create(
            data={test: {self.formulation: NO}}, name="F6", cycle=start
        )
        Score.objects.create(
            data={test: {self.formulation: NOT_REPORTING}}, name="F7", cycle=start
        )
        Score.objects.create(
            data={test: {self.formulation: NOT_REPORTING}}, name="F8", cycle=start
        )
        response = self.app.get(self.get_url(end, start, url), user="testuser")
        self.assertEqual(200, response.status_code)
        json_content = response.content.decode("utf8")
        data = json.loads(json_content)
        self.assertEquals(
            data["values"][0],
            {u"cycle": u"Mar - Apr 2015", u"no": 40, u"not_reporting": 40, u"yes": 20},
        )


class OrderFormFreeOfGapsViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 6
    formulation = DEFAULT

    def get_url(self, end, start, url):
        regimen = DEFAULT
        return "%s?start=%s&&end=%s&&regimen=%s" % (url, start, end, regimen)


class DifferentOrdersOverTimeViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 9


class ClosingBalanceViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 10


class StableConsumptionViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 11


class WarehouseFulfilmentViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 12


class StablePatientVolumesViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 8


class GuideLineAdherenceViewTestCase(OrderFormFreeOfNegativesViewTestCase):
    test_id = 2
    formulation = "Paed 1L"

    def get_url(self, end, start, url):
        regimen = "Paed 1L"
        return "%s?start=%s&end=%s&regimen=%s" % (url, start, end, regimen)

    def test_view_is_wired_up(self):
        pass
