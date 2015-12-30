import json

from django.core.urlresolvers import reverse
from django_webtest import WebTest
from model_mommy import mommy

from dashboard.models import DashboardUser, IIP, DISTRICT, WAREHOUSE, Cycle
from locations.models import District, WareHouse, IP


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
        ips = mommy.make(IP, _quantity=5)
        districts = mommy.make(District, _quantity=10)
        warehouses = mommy.make(WareHouse, _quantity=13)
        cycles = mommy.make(Cycle, _quantity=13)
        expected_warehouses = [{"pk": warehouse.pk, "name": warehouse.name} for warehouse in sorted(warehouses, key=lambda x: x.name)]
        expected_ips = [{"pk": ip.pk, "name": ip.name} for ip in sorted(ips, key=lambda x: x.name)]
        expected_districts = [{"pk": dis.pk, "name": dis.name} for dis in sorted(districts, key=lambda x: x.name)]
        expected_cycles = [{"cycle": cy.cycle} for cy in sorted(cycles, key=lambda x: x.cycle)]
        url = reverse("filters")
        response = self.app.get(url)
        data = json.loads(response.content)
        self.assertEquals(data['cycles'], expected_cycles)
        self.assertEquals(data['districts'], expected_districts)
        self.assertEquals(data['warehouses'], expected_warehouses)
        self.assertEqual(data['ips'], expected_ips)


class CyclesViewTestCase(WebTest):
    def test_cycles(self):
        cycle = mommy.make(Cycle, cycle="May - Jun 2015")
        url = reverse("cycles")
        response = self.app.get(url)
        data = json.loads(response.content)
        self.assertTrue(cycle.cycle in data['values'])
