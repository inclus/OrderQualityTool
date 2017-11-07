import pygogo

from dashboard.data.entities import ReportOutput
from dashboard.medist.scrapper import DHIS2Scrapper

logger = pygogo.Gogo(__name__).get_structured_logger()


def fetch_reports(reports, period):
    scrapper = DHIS2Scrapper()
    results = []
    for report in reports:
        report_id = report.report_id
        if report_id:
            report_html = scrapper.get_standard_report(report_id, period, report.org_unit_id)
            results.append(ReportOutput(output=report_html, report=report))
        else:
            logger.info("Report has no id", extra=report)
    return results
