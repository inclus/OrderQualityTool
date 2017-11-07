import djclick as click

from dashboard.data.data_import import ExcelDataImport
from dashboard.management.commands.manual_check import export_results, perform_checks
from dashboard.models import Cycle
from dashboard.tasks import run_checks, persist_scores


@click.command()
@click.argument('cycle')
def command(cycle):
    data = Cycle.objects.filter(title=cycle)
    for cycle in data:
        report = ExcelDataImport(None, cycle.title).build_form_db(cycle)
        run_checks(report)
        persist_scores(report)
    export_results()
