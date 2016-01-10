import os

import pydash
from celery import shared_task

from dashboard.data.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckPaed1L
from dashboard.data.adherence import GuidelineAdherenceCheckAdult2L
from dashboard.data.blanks import BlanksQualityCheck, MultipleCheck, WebBasedCheck, IsReportingCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.cycles import CLOSINGBALANCEMATCHESOPENINGBALANCECheck, STABLEPATIENTVOLUMESCheck, WAREHOUSEFULFILMENTCheck, STABLECONSUMPTIONCheck, DIFFERENTORDERSOVERTIMECheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.data.nn import NNRTICURRENTADULTSCheck, NNRTINewAdultsCheck, NNRTINEWPAEDCheck
from dashboard.data.nn import NNRTICURRENTPAEDCheck
from dashboard.data.utils import facility_has_single_order
from dashboard.helpers import YES, to_date, format_range
from dashboard.models import CycleFormulationScore, Score, Cycle, Consumption, AdultPatientsRecord, PAEDPatientsRecord, MultipleOrderFacility


def get_prev_cycle(cycle):
    current_cycle_date = to_date(cycle)
    start_month = current_cycle_date.replace(months=-3)
    end_month = current_cycle_date.replace(months=-2)
    prev_cycle = format_range(start_month, end_month)
    return prev_cycle


def persist_consumption(report):
    persist_records(report.locs, Consumption, report.cs, report.cycle)


def persist_adult_records(report):
    persist_records(report.locs, AdultPatientsRecord, report.ads, report.cycle)


def persist_paed_records(report):
    persist_records(report.locs, PAEDPatientsRecord, report.pds, report.cycle)


def persist_records(locs, model, collection, cycle):
    adult_records = []
    for facility in locs:
        facility_name = facility.get('name', None)
        records = collection.get(facility_name)
        ip = facility.get('IP', None)
        district = facility.get('District', None)
        warehouse = facility.get('Warehouse', None)
        for r in records:
            c = model(
                    name=facility_name,
                    ip=ip,
                    district=district,
                    warehouse=warehouse,
                    cycle=cycle,
                    **r
            )
            adult_records.append(c)
    model.objects.filter(cycle=cycle).delete()
    model.objects.bulk_create(adult_records)


def build_mof(report):
    def func(facility):
        facility_name = facility.get('name', None)
        ip = facility.get('IP', None)
        district = facility.get('District', None)
        warehouse = facility.get('Warehouse', None)
        return MultipleOrderFacility(
                cycle=report.cycle,
                name=facility_name,
                ip=ip,
                district=district,
                warehouse=warehouse)

    return func


def persist_multiple_order_records(report):
    facilities_with_multiple_orders = pydash.reject(report.locs, lambda f: facility_has_single_order(f))
    all = pydash.collect(facilities_with_multiple_orders, build_mof(report))
    MultipleOrderFacility.objects.filter(cycle=report.cycle).delete()
    MultipleOrderFacility.objects.bulk_create(all)


@shared_task
def calculate_scores_for_checks_in_cycle(report):
    run_checks_and_persist_formulation_scores(report)
    persist_scores(report)
    persist_consumption(report)
    persist_adult_records(report)
    persist_paed_records(report)
    persist_multiple_order_records(report)


def run_checks_and_persist_formulation_scores(report):
    formulation_scores = list()
    one_cycle_checks = [
        BlanksQualityCheck,
        NegativeNumbersQualityCheck,
        ConsumptionAndPatientsQualityCheck,
        MultipleCheck,
        WebBasedCheck,
        IsReportingCheck,
        GuidelineAdherenceCheckAdult1L,
        GuidelineAdherenceCheckAdult2L,
        GuidelineAdherenceCheckPaed1L,
        NNRTICURRENTADULTSCheck,
        NNRTICURRENTPAEDCheck,
        NNRTINewAdultsCheck,
        NNRTINEWPAEDCheck
    ]
    for check in one_cycle_checks:
        score = check(report).score()
        formulation_scores.extend(score)
    other_report = get_report_for_other_cycle(report)
    two_cycle_checks = [CLOSINGBALANCEMATCHESOPENINGBALANCECheck,
                        DIFFERENTORDERSOVERTIMECheck,
                        STABLECONSUMPTIONCheck,
                        WAREHOUSEFULFILMENTCheck,
                        STABLEPATIENTVOLUMESCheck
                        ]
    for check in two_cycle_checks:
        score = check(report, other_report).score()
        formulation_scores.extend(score)
    CycleFormulationScore.objects.filter(cycle=report.cycle).delete()
    CycleFormulationScore.objects.bulk_create(formulation_scores)


def get_report_for_other_cycle(report):
    prev_cycle_title = get_prev_cycle(report.cycle)
    other_report = FreeFormReport(None, prev_cycle_title)
    if Cycle.objects.filter(title=prev_cycle_title).exists():
        prev_cycle = Cycle.objects.get(title=prev_cycle_title)
        other_report = other_report.build_form_db(prev_cycle)
    return other_report


def persist_scores(report):
    scores = list()
    for facility in report.locs:
        s = Score(
                name=facility.get('name', None),
                ip=facility.get('IP', None),
                district=facility.get('District', None),
                warehouse=facility.get('Warehouse', None),
                cycle=report.cycle,
                fail_count=0,
                pass_count=0)
        for key, value in facility['scores'].items():
            setattr(s, key, value)
            for f, result in value.items():
                if result == YES:
                    s.pass_count += 1
                else:
                    s.fail_count += 1

        scores.append(s)
    Score.objects.filter(cycle=report.cycle).delete()
    Score.objects.bulk_create(scores)


@shared_task
def import_general_report(path, cycle):
    report = FreeFormReport(path, cycle).load()
    report.save()
    os.remove(path)
    calculate_scores_for_checks_in_cycle(report)
