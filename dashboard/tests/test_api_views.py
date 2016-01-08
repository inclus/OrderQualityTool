import json
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from model_mommy import mommy
from dashboard.models import DashboardUser, IIP, DISTRICT, WAREHOUSE, Cycle, Score


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
            data = json.loads(response.content)
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
        data = json.loads(response.content)
        self.assertEquals(data['cycles'], expected_cycles)
        self.assertEquals(data['districts'], expected_districts)
        self.assertEquals(data['warehouses'], expected_warehouses)
        self.assertEqual(data['ips'], expected_ips)


class CyclesViewTestCase(WebTest):
    def test_cycles(self):
        score = Score.objects.create(cycle="May - Jun 2015")
        url = reverse("cycles")
        response = self.app.get(url)
        data = json.loads(response.content)
        self.assertTrue(score.cycle in data['values'])
