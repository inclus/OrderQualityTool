import pygogo
from bs4 import BeautifulSoup
from splinter import Browser

from dashboard.helpers import HTML_PARSER
from dashboard.data.html_data_import import TR, TD

logger = pygogo.Gogo(__name__).get_structured_logger()


def get_html_table(html_doc, report_id):
    soup = BeautifulSoup(html_doc, HTML_PARSER)
    tables = soup.find_all('table')
    if len(tables) > 0:
        logger.debug("found tables", extra={"count": len(tables), "report_id": report_id})
        largest = tables[0]
        for table in filter(lambda t: t != largest, tables):
            rows = table.findChildren([TD, TR])
            rows_in_largest = largest.findChildren([TR, TD])
            if len(rows) > len(rows_in_largest):
                largest = table
        return largest
    logger.debug("No table found for %s", report_id)
    return None


class DHIS2Scrapper(object):
    def __init__(self):
        from django.conf import settings
        username = settings.DHIS2_USERNAME
        password = settings.DHIS2_PASSWORD
        base_url = settings.DHIS2_URL
        self.base_url = base_url

        browser = Browser('phantomjs')
        login_url = "%s/dhis-web-commons/security/login.action" % base_url
        logger.debug("login", extra={"url": login_url})

        browser.visit(login_url)

        browser.fill(USERNAME_FIELD, username)
        browser.fill(PASSWORD_FIELD, password)
        button = browser.find_by_css('input.button')
        button.click()
        log_context = {"login_url": login_url, "username": username, "browser_url": browser.url}
        login_succeeded = len(browser.find_by_text('Log out')) > 0
        if login_succeeded:
            logger.debug("login success", extra=log_context)
            self.browser = browser
        else:
            logger.debug("login failed", extra=log_context)
            raise Exception("dhis2 login failed")

    def get_standard_report(self, report_id, period, org_unit):
        query = {
            BASE_URL: self.base_url,
            REPORT_ID: report_id,
            ORG_UNIT: org_unit,
            PERIOD: period
        }
        url = "%(base_url)s/dhis-web-reporting/generateHtmlReport.action?uid=%(report_id)s&pe=%(period)s&ou=%(org_unit)s" % query
        logger.info("open report", extra=query)
        self.browser.visit(url)
        return get_html_table(self.browser.html, report_id)


PERIOD = "period"
ORG_UNIT = "org_unit"
REPORT_ID = "report_id"
BASE_URL = "base_url"
PASSWORD_FIELD = 'j_password'
USERNAME_FIELD = 'j_username'