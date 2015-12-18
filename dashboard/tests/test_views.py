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


class BestDistrictReportingView(WebTest):
    def test_best_performing_districts(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse, ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        url = reverse("ranking_best")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        print data, Score.objects.all()
        self.assertEquals('dis1', data[0]['name'])
        self.assertEquals(100, data[0]['rate'])

    def test_worst_performing_districts(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse, ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        url = reverse("ranking_worst")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('dis2', data[0]['name'])
        self.assertEquals(50, data[0]['rate'])


class ReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse, ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        self.assertEqual(3, Score.objects.count())
        filters = {}
        filters[REPORTING] = "YES"
        self.assertEqual(2, Score.objects.filter(**filters).count())


class WebBasedReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse, ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, web_based=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, web_based=False)
        WebBasedReportingCheck().run(cycle)
        self.assertEqual(3, Score.objects.count())
        filters = {}
        filters[WEB_BASED] = "YES"
        self.assertEqual(2, Score.objects.filter(**filters).count())


class MultipleReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        ip, _ = IP.objects.get_or_create(name="ip")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, warehouse=warehouse, ip=ip)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2, warehouse=warehouse, ip=ip)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2, warehouse=warehouse, ip=ip)
        Cycle.objects.create(facility=loc, cycle=cycle, multiple=True)
        Cycle.objects.create(facility=loc2, cycle=cycle, multiple=True)
        Cycle.objects.create(facility=loc3, cycle=cycle, multiple=False)
        MultipleOrdersCheck().run(cycle)
        self.assertEqual(3, Score.objects.count())
        filters = {}
        filters[MULTIPLE_ORDERS] = "YES"
        self.assertEqual(2, Score.objects.filter(**filters).count())


class FacilityTestCycleScoresListViewTestCase(WebTest):
    def xtest_should_make_one_query(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        cycle2 = 'Mar - Apr %s' % now().format("YYYY")
        dis, _ = District.objects.get_or_create(name="dis1")
        ip, _ = IP.objects.get_or_create(name="ip")
        warehouse, _ = WareHouse.objects.get_or_create(name="warehouse")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis, ip=ip, warehouse=warehouse)
        cycle_record = Cycle.objects.create(facility=loc, cycle=cycle, multiple=True)
        cycle_record_2 = Cycle.objects.create(facility=loc, cycle=cycle2, multiple=True)
        Score.objects.create(facility_cycle=cycle_record, test="TEST1", score="YES", formulation="formulation1")
        Score.objects.create(facility_cycle=cycle_record, test="TEST2", score="NO", formulation="formulation1")
        Score.objects.create(facility_cycle=cycle_record, test="TEST2", score="NO", formulation="formulation2")
        with self.assertNumQueries(1):
            response = self.app.get(reverse("scores"))
            json_text = response.content.decode('utf8')
            data = json.loads(json_text)
            self.assertEqual(len(data['results']), 3)
            self.assertEqual(data['results'][0]['name'], 'AIC Jinja Special Clinic')
            self.assertEqual(data['results'][0]['warehouse'], 'warehouse')
            self.assertEqual(data['results'][0]['district'], 'district')
            self.assertEqual(data['results'][0]['ip'], 'ip')
            self.assertEqual(data['results'][0]['score'], 'YES')
