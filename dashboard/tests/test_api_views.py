import json

from arrow import now
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from model_mommy import mommy

from dashboard.helpers import DEFAULT, YES, NO
from dashboard.models import DashboardUser, IIP, DISTRICT, WAREHOUSE, Score


class RankingsAccessViewTestCase(WebTest):
    def test_should_not_show_ip_if_access_level_is_ip(self):
        url = reverse('rankings-access')
        cases = [
            {"level": IIP, "values": ['District', 'Warehouse', 'Facility']},
            {"level": DISTRICT, "values": ['IP', 'Warehouse', 'Facility']},
            {"level": WAREHOUSE, "values": ['District', 'IP', 'Facility']},
        ]
        for case in cases:
            user = mommy.make(DashboardUser, access_level=case['level'])
            response = self.app.get(url, user=user)
            data = json.loads(response.content.decode('utf8'))
            self.assertEquals(data['values'], case['values'])


class FilterValuesViewTestCase(WebTest):
    def test_filters(self):
        Score.objects.create(warehouse='warehouse1', ip='ip1', district='district1', name="fa", cycle="Ja")
        Score.objects.create(warehouse='warehouse2', ip='ip1', district='district1', name="fa", cycle="Ja")
        expected_warehouses = [{'warehouse': 'warehouse1'}, {'warehouse': 'warehouse2'}]
        expected_ips = [{'ip': 'ip1'}]
        expected_districts = [{'district': 'district1'}]
        expected_cycles = [{'cycle': 'Ja'}]
        url = reverse("filters")
        response = self.app.get(url)
        data = json.loads(response.content.decode('utf8'))
        self.assertEquals(data['cycles'], expected_cycles)
        self.assertEquals(data['districts'], expected_districts)
        self.assertEquals(data['warehouses'], expected_warehouses)
        self.assertEqual(data['ips'], expected_ips)


class CyclesViewTestCase(WebTest):
    def test_cycles(self):
        current_year = str(now().year)
        score = Score.objects.create(cycle="May - Jun %s" % current_year)
        url = reverse("cycles")
        response = self.app.get(url)
        data = json.loads(response.content.decode('utf8'))
        self.assertTrue(score.cycle in data['values'])


class ReportingRateAggregateViewTestCase(WebTest):
    def test_should_only_consider_faciilites_user_has_access_to(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        Score.objects.create(name="F1", ip="IP1", cycle=cycle, data={"Facility Reporting": {DEFAULT: YES}})
        Score.objects.create(name="F2", ip="IP1", cycle=cycle, data={"Facility Reporting": {DEFAULT: NO}})
        user = mommy.make(DashboardUser, access_level='IP', access_area='IP1')
        response = self.app.get("/api/test/1/", user=user)
        data = json.loads(response.content.decode('utf8'))['values']
        self.assertIn({"yes": 50, "cycle": cycle, "no": 50, "not_reporting": 0}, data)
