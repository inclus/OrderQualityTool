from django_webtest import WebTest
from django.core.urlresolvers import reverse
from nose_parameterized import parameterized
from dashboard.models import Score, DashboardUser
import random
from model_mommy import mommy

class ReportViewTestCase(WebTest):
    def test_should_require_login_to_view(self):
        url_name = "reports"
        response = self.app.get(reverse(url_name))
        self.assertEquals(response.status_code , 302)

    def test_should_route_correctly(self):
        url_name = "reports"
        response = self.app.get(reverse(url_name), user="james")
        self.assertEquals(response.status_code , 200)

    @parameterized.expand([
        ("districts", "district", ["place1", "place2", "place2"], 2),
        ("districts", "district", ["place2"], 1),
        ("ips", "ip", ["place1", "place2", "place2"], 2),
        ("warehouses", "warehouse", ["ware1", "ware2"], 2),
        ("cycles", "cycle", ["Jul - Oct 2015", "Sep - Oct 2015"], 2),
    ])
    def test_should_have_values_for(self, test_case_name, model, names, expected):
        for name in names:
            data = {model: name, "name": "name-%s" % random.randint(2, 99)}
            Score.objects.create(**data)
        url_name = "reports"
        response = self.app.get(reverse(url_name), user="james")
        self.assertEquals(response.status_code , 200)
        data = response.context[test_case_name]
        self.assertEquals(len(data), expected)


    @parameterized.expand([
        ("districts", "district", ["place1", "place2", "place2"], 1),
        ("ips", "ip", ["place1", "place2", "place2"], 1),
        ("warehouses", "warehouse", ["ware1", "ware2"], 1)
    ])
    def test_should_limit_access_to_place(self, test_case_name, model, names, expected):
        user = mommy.make(DashboardUser,access_level = model, access_area = names[0])
        for name in names:
            data = {model: name, "name": "name-%s" % random.randint(2, 99)}
            Score.objects.create(**data)
        url_name = "reports"
        response = self.app.get(reverse(url_name), user=user)
        self.assertEquals(response.status_code , 200)
        data = response.context[test_case_name]
        self.assertEquals(len(data), expected)

