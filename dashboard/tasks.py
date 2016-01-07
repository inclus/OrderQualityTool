import os
import time
from celery import shared_task

from dashboard.data.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckPaed1L
from dashboard.data.adherence import GuidelineAdherenceCheckAdult2L
from dashboard.data.blanks import BlanksQualityCheck, MultipleCheck, WebBasedCheck, IsReportingCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.nn import NNRTICURRENTADULTSCheck, NNRTINewAdultsCheck, NNRTINEWPAEDCheck
from dashboard.data.nn import NNRTICURRENTPAEDCheck
from dashboard.helpers import YES
from dashboard.models import CycleFormulationScore, Score


@shared_task
def process_test(check_class, cycle):
    result = check_class().run(cycle)
    return result


@shared_task
def calculate_scores_for_checks_in_cycle(report):
    formulation_scores = list()
    formulation_scores.extend(BlanksQualityCheck(report).score())
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

    os.remove(path)
    calculate_scores_for_checks_in_cycle(report)
