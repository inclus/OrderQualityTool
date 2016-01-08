import os
import time
from celery import shared_task
from dashboard.data.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckPaed1L
from dashboard.data.adherence import GuidelineAdherenceCheckAdult2L
from dashboard.data.blanks import BlanksQualityCheck, MultipleCheck, WebBasedCheck, IsReportingCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.cycles import DIFFERENTORDERSOVERTIMECheck, CLOSINGBALANCEMATCHESOPENINGBALANCECheck, \
    STABLECONSUMPTIONCheck, WAREHOUSEFULFILMENTCheck, STABLEPATIENTVOLUMESCheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.data.nn import NNRTICURRENTADULTSCheck, NNRTINewAdultsCheck, NNRTINEWPAEDCheck
from dashboard.data.nn import NNRTICURRENTPAEDCheck
from dashboard.helpers import YES, to_date, format_range
from dashboard.models import CycleFormulationScore, Score, Cycle


@shared_task
def process_test(check_class, cycle):
    result = check_class().run(cycle)
    return result


def get_prev_cycle(cycle):
    current_cycle_date = to_date(cycle)
    start_month = current_cycle_date.replace(months=-3)
    end_month = current_cycle_date.replace(months=-2)
    prev_cycle = format_range(start_month, end_month)
    return prev_cycle


@shared_task
def calculate_scores_for_checks_in_cycle(report):
    formulation_scores = list()
    formulation_scores.extend(BlanksQualityCheck(report).score())
    formulation_scores.extend(NegativeNumbersQualityCheck(report).score())
    formulation_scores.extend(ConsumptionAndPatientsQualityCheck(report).score())
    formulation_scores.extend(MultipleCheck(report).score())
    formulation_scores.extend(WebBasedCheck(report).score())
    formulation_scores.extend(IsReportingCheck(report).score())
    formulation_scores.extend(GuidelineAdherenceCheckAdult1L(report).score())
    formulation_scores.extend(GuidelineAdherenceCheckAdult2L(report).score())
    formulation_scores.extend(GuidelineAdherenceCheckPaed1L(report).score())
    formulation_scores.extend(NNRTICURRENTADULTSCheck(report).score())
    formulation_scores.extend(NNRTICURRENTPAEDCheck(report).score())
    formulation_scores.extend(NNRTINewAdultsCheck(report).score())
    formulation_scores.extend(NNRTINEWPAEDCheck(report).score())
    prev_cycle_title = get_prev_cycle(report.cycle)
    other_report = FreeFormReport(None, prev_cycle_title)
    if Cycle.objects.filter(title=prev_cycle_title).exists():
        prev_cycle = Cycle.objects.get(title=prev_cycle_title)
        other_report = other_report.build_form_db(prev_cycle)
    formulation_scores.extend(CLOSINGBALANCEMATCHESOPENINGBALANCECheck(report, other_report).score())
    # formulation_scores.extend(DIFFERENTORDERSOVERTIMECheck(report, other_report).score())
    # formulation_scores.extend(STABLECONSUMPTIONCheck(report, other_report).score())
    # formulation_scores.extend(WAREHOUSEFULFILMENTCheck(report, other_report).score())
    # formulation_scores.extend(STABLEPATIENTVOLUMESCheck(report, other_report).score())
    CycleFormulationScore.objects.filter(cycle=report.cycle).delete()
    CycleFormulationScore.objects.bulk_create(formulation_scores)

    scores = list()
    for facility in report.locs:
        s = Score(name=facility['name'], ip=facility['IP'], district=facility['District'],
                  warehouse=facility['Warehouse'], cycle=report.cycle, fail_count=0, pass_count=0)
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
