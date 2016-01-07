import logging

import djclick as click

from dashboard.data.adherence import GuidelineAdherenceCheckPaed1L, GuidelineAdherenceCheckAdult2L, \
    GuidelineAdherenceCheckAdult1L
from dashboard.data.blanks import BlanksQualityCheck, MultipleCheck, WebBasedCheck, IsReportingCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.nn import NNRTICURRENTADULTSCheck, NNRTINewAdultsCheck, NNRTICURRENTPAEDCheck, NNRTINEWPAEDCheck
from dashboard.helpers import F1

logger = logging.getLogger(__name__)


@click.command()
@click.argument('path')
@click.argument('cycle')
def command(path, cycle):
    click.secho('Importing {}'.format(path), fg='red')
    report = FreeFormReport(path, cycle).load()
    print len(report.cs)
    print "Blanks :", BlanksQualityCheck(report).run()['DEFAULT']['YES']
    print "ConsumptionAndPatients :", ConsumptionAndPatientsQualityCheck(report).run()[F1]['YES']
    print "Multiple :", MultipleCheck(report).run()['DEFAULT']['YES']
    print "Web :", WebBasedCheck(report).run()['DEFAULT']['YES']
    print "Reporting :", IsReportingCheck(report).run()['DEFAULT']['YES']
    print "Adherence Adult 1L :", GuidelineAdherenceCheckAdult1L(report).run()['DEFAULT']['YES']
    print "Adherence Adult 2L :", GuidelineAdherenceCheckAdult2L(report).run()['DEFAULT']['YES']
    print "Adherence Paed 1L :", GuidelineAdherenceCheckPaed1L(report).run()['DEFAULT']['YES']
    print "NNRTI CurrentAdult :", NNRTICURRENTADULTSCheck(report).run()['DEFAULT']['YES']
    print "NNRTI CurrentPaed :", NNRTICURRENTPAEDCheck(report).run()['DEFAULT']['YES']
    print "NNRTI NewAdult :", NNRTINewAdultsCheck(report).run()['DEFAULT']['YES']
    print "NNRTI NewPaed :", NNRTINEWPAEDCheck(report).run()['DEFAULT']['YES']
