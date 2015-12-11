import os
from json import loads

from arrow import now
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_webtest import WebTest
from mock import patch, ANY
from webtest import Upload

from dashboard.checks.web_based_reporting import ReportingCheck, WebBasedReportingCheck, MultipleOrdersCheck
from dashboard.models import FacilityCycleRecord, FacilityCycleRecordScore
from locations.models import Facility, District


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

    @patch('dashboard.views.import_general_report.delay')
    def test_valid_form_starts_import_process(self, mock_method):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        url = '/import/'
        import_page = self.app.get(url, user="testuser")
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
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc2, cycle=cycle, reporting_status=False)
        url = "/api/test/submittedOrder"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertIn({"reporting": 50, "cycle": cycle, "not_reporting": 50}, data)


class BestDistrictReportingView(WebTest):
    def test_best_performing_districts(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2)
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        url = reverse("ranking_best")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        print data, FacilityCycleRecordScore.objects.all()
        self.assertEquals('dis1', data[0]['name'])
        self.assertEquals(100, data[0]['rate'])

    def test_worst_performing_districts(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2)
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        url = reverse("ranking_worst")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('dis2', data[0]['name'])
        self.assertEquals(50, data[0]['rate'])


class ReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2)
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc2, cycle=cycle, reporting_status=True)
        FacilityCycleRecord.objects.create(facility=loc3, cycle=cycle, reporting_status=False)
        ReportingCheck().run(cycle)
        self.assertEqual(3, FacilityCycleRecordScore.objects.count())
        self.assertEqual(2, FacilityCycleRecordScore.objects.filter(score="YES").count())


class WebBasedReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2)
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle, web_based=True)
        FacilityCycleRecord.objects.create(facility=loc2, cycle=cycle, web_based=True)
        FacilityCycleRecord.objects.create(facility=loc3, cycle=cycle, web_based=False)
        WebBasedReportingCheck().run(cycle)
        self.assertEqual(3, FacilityCycleRecordScore.objects.count())
        self.assertEqual(2, FacilityCycleRecordScore.objects.filter(score="YES").count())


class MultipleReportingCheckTestCase(TestCase):
    def test_logic(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        dis, _ = District.objects.get_or_create(name="dis1")
        dis2, _ = District.objects.get_or_create(name="dis2")
        loc, _ = Facility.objects.get_or_create(name="AIC Jinja Special Clinic", district=dis)
        loc2, _ = Facility.objects.get_or_create(name="AIC Special Clinic", district=dis2)
        loc3, _ = Facility.objects.get_or_create(name="AIC Specialic", district=dis2)
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle, multiple=True)
        FacilityCycleRecord.objects.create(facility=loc2, cycle=cycle, multiple=True)
        FacilityCycleRecord.objects.create(facility=loc3, cycle=cycle, multiple=False)
        MultipleOrdersCheck().run(cycle)
        self.assertEqual(3, FacilityCycleRecordScore.objects.count())
        self.assertEqual(2, FacilityCycleRecordScore.objects.filter(score="YES").count())
