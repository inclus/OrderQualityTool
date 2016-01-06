import logging

import djclick as click

from dashboard.data.blanks import BlanksQualityCheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.negatives import NegativeNumbersQualityCheck

logger = logging.getLogger(__name__)


@click.command()
@click.argument('path')
@click.argument('cycle')
def command(path, cycle):
    click.secho('Importing {}'.format(path), fg='red')
    report = FreeFormReport(path, cycle).load()
    print len(report.cs)
    print BlanksQualityCheck(report).run()
