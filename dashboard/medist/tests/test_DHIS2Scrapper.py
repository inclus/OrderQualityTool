from django.test import TestCase

from mock import patch, mock
from nose_parameterized import parameterized

from dashboard.medist.scrapper import DHIS2Scrapper, get_html_table

body_with_two_tables = """<html>
            <table id="123">
                <tr></tr>
                <tr></tr>
            </table>
            <table id="3434">
                <tr></tr>
                <tr></tr>
                <tr></tr>
                <tr></tr>
            </table>
        <html>"""
body_with_one_table = """<html>
            <table id="123">
                <tr></tr>
                <tr></tr>
            </table>
        <html>"""


def build_fake_browser(mock_browser_class):
    fake_browser = mock.MagicMock(name="browser")
    find_by_text_mock = mock.MagicMock()
    find_by_text_mock.return_value = [1]
    fake_browser.find_by_text = find_by_text_mock
    mock_browser_class.return_value = fake_browser
    return fake_browser


class TestDHIS2Scrapper(TestCase):
    @patch("dashboard.medist.scrapper.Browser", autospec=True)
    def test_that_scrapper_generates_correct_login_url(self, mock_browser_class):
        with self.settings(DHIS2_URL='http://dhis2.web'):
            fake_browser = build_fake_browser(mock_browser_class)
            DHIS2Scrapper()
            mock_browser_class.assert_called_with("phantomjs")
            fake_browser.visit.assert_called_with("http://dhis2.web/dhis-web-commons-about/about.action")

    @patch("dashboard.medist.scrapper.Browser", autospec=True)
    def test_that_scrapper_generates_correct_report_url(self, mock_browser_class):
        with self.settings(DHIS2_URL='http://dhis2.web'):
            fake_browser = build_fake_browser(mock_browser_class)
            fake_browser.html = "<html></html>"
            scrapper = DHIS2Scrapper()
            scrapper.get_standard_report("1", "May", "home")
            fake_browser.visit.assert_called_with(
                "http://dhis2.web/dhis-web-reporting/generateHtmlReport.action?uid=1&pe=May&ou=home")

    @parameterized.expand([
        ("has_two_tables", body_with_two_tables, "3434"),
        ("has_one_table", body_with_one_table, "123"),
    ])
    def test_get_html_table(self, test_case_name, input, expected):
        table = get_html_table(input, "fakeid")
        self.assertEqual(table.get("id"), expected)
