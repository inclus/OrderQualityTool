import logging

import djclick as click

from dashboard.tasks import calculate_scores_for_checks_in_cycle, load_report, save_report

logger = logging.getLogger(__name__)


@click.command()
@click.argument('path')
@click.argument('cycle')
def command(path, cycle):
    click.secho('Importing {}'.format(path), fg='red')
    report = load_report(cycle, path)
    save_report(report)
    calculate_scores_for_checks_in_cycle(report)
