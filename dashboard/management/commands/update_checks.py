import djclick as click

from dashboard.data.free_form_report import FreeFormReport
from dashboard.management.commands.manual_check import export_results
from dashboard.models import Cycle
from dashboard.tasks import run_checks, persist_scores


@click.command()
@click.argument('cycle')
def command(cycle):
    data = Cycle.objects.filter(title=cycle)
    for cycle in data:
        report = FreeFormReport(None, cycle.title).build_form_db(cycle)
        run_checks(report)
        persist_scores(report)
    export_results()
