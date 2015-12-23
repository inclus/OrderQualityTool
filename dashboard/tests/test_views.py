import json
import os
from json import loads

from arrow import now
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_webtest import WebTest
from mock import patch, ANY
from webtest import Upload

from dashboard.checks.web_based_reporting import ReportingCheck, WebBasedReportingCheck, MultipleOrdersCheck
from dashboard.helpers import WEB_BASED, REPORTING, MULTIPLE_ORDERS
from dashboard.models import Cycle, Score, DashboardUser
from locations.models import Facility, District, IP, WareHouse


class HomeViewTestCase(WebTest):
    def test_correct_template(self):
        home = self.app.get('/', user="testuser")
        self.assertTemplateUsed(home, "home.html")

    def test_home_requires_login(self):
        home = self.app.get('/')
        self.assertEqual(302, home.status_code)


class DataImportViewTestCase(WebTest):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path

    @patch('dashboard.views.main.import_general_report.delay')
    def test_valid_form_starts_import_process(self, mock_method):
        user = DashboardUser.objects.create_superuser("a@a.com", "secret")
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        url = '/import/'
        import_page = self.app.get(url, user=user)
        form = import_page.form
        form['cycle'] = cycle
        form['import_file'] = Upload(self.get_fixture_path("c.xlsx"))
        form.submit()
        mock_method.assert_called_with(ANY, cycle)


class FacilitiesReportingView(WebTest):
    def test_that_cycles_are_padded(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic")
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic")
        Cycle.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, reporting_status=False)
        url = "/api/test/submittedOrder"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertIn({"reporting": 50, "cycle": cycle, "not_reporting": 50}, data)

    def test_that_start_end_work(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        cycle_2 = 'Mar - Apr %s' % now().format("YYYY")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic")
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic")
        Cycle.objects.create(facility=loc, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, web_based=False)
        url = "/api/test/submittedOrder?start=%s&end=%s" % (cycle, cycle_2)
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEqual(len(data), 2)


class WebBasedReportingViewTestCase(WebTest):
    def test_that_cycles_are_padded(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic")
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic")
        Cycle.objects.create(facility=loc, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, web_based=False)
        url = "/api/test/orderType"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertIn({"web": 50, "cycle": cycle, "paper": 50}, data)

    def test_that_start_end_work(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        cycle_2 = 'Mar - Apr %s' % now().format("YYYY")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic")
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic")
        Cycle.objects.create(facility=loc, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, web_based=False)
        url = "/api/test/orderType?start=%s&end=%s" % (cycle, cycle_2)
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEqual(len(data), 2)


class FacilitiesMultipleReportingViewTestCase(WebTest):
    def test_shows_all_facilities_that_report_multiple_times(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic")
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic")
        Cycle.objects.create(facility=loc, cycle=cycle, multiple=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, web_based=False)
        url = "/api/test/facilitiesMultiple"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEqual(len(data), 1)


class BestDistrictReportingViewFor(WebTest):
    def test_best_performing_districts(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_best")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('D1', data[0]['name'])
        self.assertEquals(200.0 / 18, data[0]['rate'])
        self.assertEquals('D2', data[1]['name'])
        self.assertEquals(100.0 / 18, data[1]['rate'])

    def test_best_performing_ips(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F1", warehouse="W1", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_best") + "?level=ip"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('I1', data[0]['name'])
        self.assertEquals(200.0 / 18, data[0]['rate'])

    def test_best_performing_warehouses(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F1", warehouse="W1", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_best") + "?level=warehouse"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('W1', data[0]['name'])
        self.assertAlmostEqual(300.0 / 36, data[0]['rate'])

    def test_best_performing_facilities(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W1", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_best") + "?level=facility"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('F1', data[0]['name'])
        self.assertEquals(200.0 / 18, data[0]['rate'])

    def test_worst_performing_districts(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W1", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_worst")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('D2', data[0]['name'])
        self.assertEquals(100.0 / 18, data[0]['rate'])

    def test_worst_performing_ips(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W1", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_worst") + "?level=ip"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('I2', data[0]['name'])
        self.assertEquals(100.0 / 18, data[0]['rate'])

    def xtest_worst_performing_warehouses(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_worst") + "?level=warehouse"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('W2', data[0]['name'])
        self.assertEquals(100.0 / 18, data[0]['rate'])

    def test_worst_performing_facilities(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_worst") + "?level=facility"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('F2', data[0]['name'])
        self.assertEquals(100.0 / 18, data[0]['rate'])

    def test_worst_csv(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_worst_csv") + "?level=facility"
        csv = self.app.get(url, user="testuser").content.decode('utf8')
        expected = """facility,reporting rate
F2,5.555555555555555
F1,11.11111111111111
"""
        self.assertEquals(csv.replace("\r", ""), expected)

    def test_best_csv(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING="YES", WEB_BASED="YES")
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING="NO", WEB_BASED="YES")
        url = reverse("ranking_best_csv") + "?level=facility"
        csv = self.app.get(url, user="testuser").content.decode('utf8')
        expected = """facility,reporting rate
F1,11.11111111111111
F2,5.555555555555555
"""
        self.assertEquals(csv.replace("\r", ""), expected)


class ReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse,
                                                ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        self.assertEqual(3, Score.objects.count())
        filters = {}
        filters[REPORTING] = {"DEFAULT":"YES"}
        self.assertEqual(2, Score.objects.filter(**filters).count())


class WebBasedReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse,
                                                ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, web_based=False)
        WebBasedReportingCheck().run(cycle)
        self.assertEqual(3, Score.objects.count())
        filters = {}
        filters[WEB_BASED] = {"DEFAULT":"YES"}
        self.assertEqual(2, Score.objects.filter(**filters).count())


class MultipleReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse,
                                                ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, multiple=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, multiple=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, multiple=False)
        MultipleOrdersCheck().run(cycle)
        self.assertEqual(3, Score.objects.count())
        filters = {}
        filters[MULTIPLE_ORDERS] = {"DEFAULT":"YES"}
        self.assertEqual(2, Score.objects.filter(**filters).count())


class FacilityTestCycleScoresListViewTestCase(WebTest):
    def test_should_make_one_query(self):
        dis, _ = District.objects.get_or_create(name="dis1")
        ip, _ = IP.objects.get_or_create(name="ip")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, ip=ip,
                                                warehouse=warehouse)
        Score.objects.create(name=loc.name, warehouse=warehouse.name, district=dis.name, ip=ip.name,
                             REPORTING={"formulation1": "YES", "formulation2": "NO"})
        with self.assertNumQueries(2):
            response = self.app.get(reverse("scores"))
            json_text = response.content.decode('utf8')
            data = json.loads(json_text)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'AIC Jinja Special Clinic')
            self.assertEqual(data['results'][0]['warehouse'], 'warehouse')
            self.assertEqual(data['results'][0]['district'], 'dis1')
            self.assertEqual(data['results'][0]['ip'], 'ip')
            self.assertEqual(data['results'][0]['REPORTING'], "{u'formulation1': u'YES', u'formulation2': u'NO'}")
