import pydash
import pygogo
from django.contrib.admin.models import LogEntry, CHANGE

from dashboard.checks.legacy.check import facility_has_single_order
from dashboard.data.data_import import ExcelDataImport
from dashboard.data.html_data_import import HtmlDataImport
from dashboard.helpers import get_prev_cycle, F1, F2, F3, DEFAULT, YES, WEB, NO
from dashboard.models import Consumption, AdultPatientsRecord, PAEDPatientsRecord, MultipleOrderFacility, DashboardUser, \
    Cycle, Score
from dashboard.utils import timeit, log_formatter

logger = pygogo.Gogo(__name__, low_formatter=log_formatter).get_logger()


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
    all = pydash.map_(facilities_with_multiple_orders, build_mof(report))
    MultipleOrderFacility.objects.filter(cycle=report.cycle).delete()
    MultipleOrderFacility.objects.bulk_create(all)


def add_log_entry(data_import):
    cycle = data_import.cycle
    source = ""
    user, created = DashboardUser.objects.get_or_create(email='background_worker@service', is_active=False)
    if type(data_import) == HtmlDataImport:
        source = "from dhis2"

    if type(data_import) == ExcelDataImport:
        source = "from excel upload"

    LogEntry.objects.create(
        user_id=user.id,
        action_flag=CHANGE,
        change_message="Completed Import for cycle %s %s" % (cycle, source),
    )


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
            cycle=cycle, data=scores)
        for key, value in scores.items():
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