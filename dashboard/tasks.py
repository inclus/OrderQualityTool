import base64
import re

import pygogo
from celery import shared_task
from io import BytesIO

from raven.contrib.django.models import client

from dashboard.checks.tasks import run_dynamic_checks
from dashboard.data.data_import import DataImport, ExcelDataImport
from dashboard.data.html_data_import import HtmlDataImport
from dashboard.data.tasks import persist_consumption, persist_adult_records, persist_paed_records, \
    persist_multiple_order_records, add_log_entry, persist_scores
from dashboard.utils import timeit, log_formatter
from dashboard.medist.tasks import fetch_reports
from dashboard.models import Cycle, Dhis2StandardReport, LocationToPartnerMapping

logger = pygogo.Gogo(__name__, low_formatter=log_formatter).get_logger()


@timeit
def calculate_scores_for_checks_in_cycle(data_import):
    # type: (DataImport) -> None
    persist_consumption(data_import)
    persist_adult_records(data_import)
    persist_paed_records(data_import)
    persist_multiple_order_records(data_import)
    scores = run_dynamic_checks(data_import)
    persist_scores(scores, data_import.cycle)
    add_log_entry(data_import)


@shared_task
def update_checks(ids):
    data = Cycle.objects.filter(id__in=ids).defer("state").all()
    logger.info("update checks for ids", extra={"ids": ids})
    for cycle in data:
        try:
            data_import = DataImport(None, cycle.title).build_form_db(cycle)
            calculate_scores_for_checks_in_cycle(data_import)
        except Exception as e:
            logger.error("error",
                         extra={
                             "exception": e.message,
                             "cycle": cycle.title})
            client.captureException()


def to_mon(first_month_match):
    months = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    }
    return months.get(first_month_match, "")


def parse_periods_from_bi_monthly_cycle(bi_monthly_cycle):
    matches = re.search("([a-zA-Z]+) - ([a-zA-Z]+) (\d{4})", bi_monthly_cycle)
    if len(matches.groups()) > 0:
        year = matches.group(3)
        second_month_match = matches.group(2)
        first_month_match = matches.group(1)
        first_month = "%s%s" % (year, to_mon(first_month_match))
        second_month = "%s%s" % (year, to_mon(second_month_match))

        return [first_month, second_month]
    return []


@shared_task
def import_data_from_dhis2(bi_monthly_cycle):
    _dhis2_import(bi_monthly_cycle)


@timeit
def _dhis2_import(bi_monthly_cycle):
    periods = parse_periods_from_bi_monthly_cycle(bi_monthly_cycle)
    reports = Dhis2StandardReport.objects.all()
    partner_mapping = LocationToPartnerMapping.get_mapping()
    results = fetch_reports(reports, periods)
    data_import = HtmlDataImport(results, bi_monthly_cycle).load(partner_mapping)
    cycle = data_import.save()
    update_checks.apply_async(args=[[cycle.id]], priority=1)


@timeit
def parse_excel_file(cycle, excel_file):
    import_file = BytesIO(base64.b64decode(excel_file))
    import_file.name = "import.xlsx"
    report = ExcelDataImport(import_file, cycle).load()
    return report


@timeit
def save_data_import(report):
    return report.save()


@shared_task
def run_manual_import(cycle, data):
    report = parse_excel_file(cycle, data)
    cycle = save_data_import(report)
    update_checks.apply_async(args=[[cycle.id]], priority=1)
    return cycle
