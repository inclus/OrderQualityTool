import logging
import djclick as click
from dashboard.data.adherence import GuidelineAdherenceCheckPaed1L, GuidelineAdherenceCheckAdult2L, \
    GuidelineAdherenceCheckAdult1L
from dashboard.data.blanks import BlanksQualityCheck, MultipleCheck, WebBasedCheck, IsReportingCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.nn import NNRTICURRENTADULTSCheck, NNRTINewAdultsCheck, NNRTICURRENTPAEDCheck, NNRTINEWPAEDCheck
from dashboard.helpers import F1
from dashboard.tasks import calculate_scores_for_checks_in_cycle

logger = logging.getLogger(__name__)


@click.command()
@click.argument('path')
@click.argument('cycle')
def command(path, cycle):
    click.secho('Importing {}'.format(path), fg='red')
    report = FreeFormReport(path, cycle).load()
    calculate_scores_for_checks_in_cycle(report)
