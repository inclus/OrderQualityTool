import pygogo

from dashboard.data.entities import ReportOutput
from dashboard.medist.client import DHIS2APIClient
from dashboard.medist.scrapper import DHIS2Scrapper
from dashboard.utils import log_formatter

logger = pygogo.Gogo(__name__, low_formatter=log_formatter).get_logger()


def fetch_reports(reports, periods):
    scrapper = DHIS2Scrapper()
    results = []
    for period in periods:
        for report in reports:
            units = DHIS2APIClient().get_children(report.org_unit_id)
            for unit in units:
                report_id = report.report_id
                if report_id:
                    report_html = scrapper.get_standard_report(report_id, period, unit)
                    if report_html:
                        results.append(ReportOutput(output=str(report_html), report=report))
                else:
                    logger.info("Report has no id", extra=report)
    return results
