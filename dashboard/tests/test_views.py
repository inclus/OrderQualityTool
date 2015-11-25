import os
from json import loads

from arrow import now
from django_webtest import WebTest
from mock import patch, ANY
from webtest import Upload

from dashboard.models import FacilityCycleRecord
from locations.models import Facility


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
        FacilityCycleRecord.objects.create(facility=loc, cycle=cycle)
        url = "/api/test/reportingRate"
        json_response = self.app.get(url, user="testuser").content
        data = loads(json_response)['values']
        self.assertIn({"count": 1, "cycle": cycle}, data)
