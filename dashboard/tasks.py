import re
from collections import defaultdict

import attr
import pydash
import pygogo
from celery import shared_task

from dashboard.data.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckPaed1L
from dashboard.data.adherence import GuidelineAdherenceCheckAdult2L
from dashboard.data.blanks import BlanksQualityCheck, MultipleCheck, IsReportingCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.cycles import BalancesMatchCheck, StablePatientVolumesCheck, WarehouseFulfillmentCheck, \
    StableConsumptionCheck, OrdersOverTimeCheck
from dashboard.data.data_import import ExcelDataImport, DataImport
from dashboard.data.entities import enrich_location_data
from dashboard.data.html_data_import import HtmlDataImport
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.data.nn import NNRTIADULTSCheck
from dashboard.data.nn import NNRTIPAEDCheck
from dashboard.data.utils import facility_has_single_order, timeit
from dashboard.helpers import YES, get_prev_cycle, WEB, F1, F2, F3, DEFAULT, NO, NAME
from dashboard.medist.tasks import fetch_reports
from dashboard.models import Score, Cycle, Consumption, AdultPatientsRecord, PAEDPatientsRecord, MultipleOrderFacility, \
    Dhis2StandardReport, LocationToPartnerMapping

logger = pygogo.Gogo(__name__).get_structured_logger()


@timeit
def persist_consumption(report):
    persist_records(report.locs, Consumption, report.cs, report.cycle)


@timeit
def persist_adult_records(report):
    persist_records(report.locs, AdultPatientsRecord, report.ads, report.cycle)


@timeit
def persist_paed_records(report):
    persist_records(report.locs, PAEDPatientsRecord, report.pds, report.cycle)


def persist_records(locs, model, collection, cycle):
    adult_records = []
    for location in locs:
        facility_name = location.facility
        records = collection.get(location, [])
        ip = location.partner
        district = location.district
        warehouse = location.warehouse
        for r in records:
            record_as_dict = r.as_dict_for_model()
            c = model(
                name=facility_name,
                ip=ip,
                district=district,
                warehouse=warehouse,
                cycle=cycle,
                **record_as_dict
            )
            adult_records.append(c)
    logger.info("saving records", extra={"cycle": cycle, "model": model.__name__, "count": len(adult_records)})
    model.objects.filter(cycle=cycle).delete()
    model.objects.bulk_create(adult_records)


def build_mof(report):
    def func(location):
        facility_name = location.facility
        ip = location.partner
        district = location.district
        warehouse = location.warehouse
        return MultipleOrderFacility(
            cycle=report.cycle,
            name=facility_name,
            ip=ip,
            district=district,
            warehouse=warehouse)

    return func


@timeit
def persist_multiple_order_records(report):
    facilities_with_multiple_orders = pydash.reject(report.locs, lambda f: facility_has_single_order(f))
    all = pydash.collect(facilities_with_multiple_orders, build_mof(report))
    MultipleOrderFacility.objects.filter(cycle=report.cycle).delete()
    MultipleOrderFacility.objects.bulk_create(all)


@timeit
def calculate_scores_for_checks_in_cycle(data_import):
    # type: (DataImport) -> None
    scores = run_checks(data_import)
    persist_scores(scores, data_import.cycle)
    persist_consumption(data_import)
    persist_adult_records(data_import)
    persist_paed_records(data_import)
    persist_multiple_order_records(data_import)


@timeit
def run_checks(report):
    scores = defaultdict(lambda: defaultdict(dict))
    other_report = get_report_for_other_cycle(report)
    checks = [
        BlanksQualityCheck(),
        NegativeNumbersQualityCheck(),
        ConsumptionAndPatientsQualityCheck(),
        MultipleCheck(),
        IsReportingCheck(),
        GuidelineAdherenceCheckAdult1L(),
        GuidelineAdherenceCheckAdult2L(),
        GuidelineAdherenceCheckPaed1L(),
        NNRTIADULTSCheck(),
        NNRTIPAEDCheck(),
        BalancesMatchCheck(),
        OrdersOverTimeCheck(),
        StableConsumptionCheck(),
        WarehouseFulfillmentCheck(),
        StablePatientVolumesCheck()
    ]
    for location in report.locs:
        facility_data = enrich_location_data(location, report)
        other_facility_data = enrich_location_data(location, other_report)
        for check in checks:
            for combination in check.combinations:
                scores[location][check.test][combination[NAME]] = check.for_each_facility(facility_data,
                                                                                          combination,
                                                                                          other_facility_data)
    return scores


@timeit
def get_report_for_other_cycle(report):
    prev_cycle_title = get_prev_cycle(report.cycle)
    other_report = ExcelDataImport(None, prev_cycle_title)
    if Cycle.objects.filter(title=prev_cycle_title).exists():
        prev_cycle = Cycle.objects.get(title=prev_cycle_title)
        other_report = other_report.build_form_db(prev_cycle)
    return other_report


@timeit
def persist_scores(score_cache, cycle):
    list_of_score_obj = list()
    mapping = {
        F1: {"pass": "f1_pass_count", "fail": "f1_fail_count"},
        F2: {"pass": "f2_pass_count", "fail": "f2_fail_count"},
        F3: {"pass": "f3_pass_count", "fail": "f3_fail_count"},
        DEFAULT: {"pass": "default_pass_count", "fail": "default_fail_count"},
    }
    for location, scores in score_cache.items():
        s = Score(
            name=location.facility,
            ip=location.partner,
            district=location.district,
            warehouse=location.warehouse,
            cycle=cycle)
        for key, value in scores.items():
            setattr(s, key, value)
            for f, result in value.items():
                formulation_mapping = mapping.get(f)
                if result in [YES, WEB]:
                    model_field = formulation_mapping.get("pass")
                    s.__dict__[model_field] += 1
                elif result in [NO]:
                    model_field = formulation_mapping.get("fail")
                    s.__dict__[model_field] += 1

        list_of_score_obj.append(s)
    Score.objects.filter(cycle=cycle).delete()
    Score.objects.bulk_create(list_of_score_obj)


@shared_task
def update_checks(ids):
    data = Cycle.objects.filter(id__in=ids).all()
    for cycle in data:
        data_import = DataImport(None, cycle.title).build_form_db(cycle)
        calculate_scores_for_checks_in_cycle(data_import)


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
        print(year, first_month_match, second_month_match)
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
    update_checks.delay([cycle.id])
