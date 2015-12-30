import djclick as click
from assertlib import assertEquals

from dashboard.checks.consumption_and_patients import ConsumptionAndPatients
from dashboard.checks.guideline_adherence import GuidelineAdherence
from dashboard.checks.nnrti_checks import NNRTI
from dashboard.checks.stable_consumption import StableConsumption
from dashboard.checks.stable_patient_volumes import StablePatientVolumes
from dashboard.models import CycleScore, CycleFormulationScore


@click.command()
@click.argument('cycle')
def command(cycle):
    click.secho('Running Check for Cycle, {}'.format(cycle), fg='red')
    check_consumption_and_patients(cycle)


def check_guideline_adherence(cycle):
    check = GuidelineAdherence()
    check.run(cycle)
    result = dict((sc.formulation, float("{0:.2f}".format(sc.yes))) for sc in CycleFormulationScore.objects.filter(cycle=cycle, test=check.test))
    click.secho('Result, {}'.format(result), fg='green')
    assertEquals(result['Adult 1L'], 27.5)
    assertEquals(result['Adult 2L'], 41.5)
    assertEquals(result['Paed 1L'], 26.8)


def check_stable_patient_volumes(cycle):
    check = StablePatientVolumes()
    check.run(cycle)
    result = dict((sc.formulation, float("{0:.2f}".format(sc.yes))) for sc in CycleFormulationScore.objects.filter(cycle=cycle, test=check.test))
    click.secho('Result, {}'.format(result), fg='green')


def check_stable_consumption(cycle):
    check = StableConsumption()
    check.run(cycle)
    result = dict((sc.formulation, float("{0:.2f}".format(sc.yes))) for sc in CycleFormulationScore.objects.filter(cycle=cycle, test=check.test))
    click.secho('Result, {}'.format(result), fg='green')


def check_consumption_and_patients(cycle):
    check = ConsumptionAndPatients()
    check.run(cycle)
    result = dict((sc.formulation, float("{0:.2f}".format(sc.yes))) for sc in CycleFormulationScore.objects.filter(cycle=cycle, test=check.test))
    click.secho('Result, {}'.format(result), fg='green')


def check_nnrti(cycle):
    check = NNRTI()

    check.run(cycle)
    result = dict((sc.test, float("{0:.2f}".format(sc.yes))) for sc in CycleScore.objects.filter(cycle=cycle, test__icontains="nnrti"))
    click.secho('Result, {}'.format(result), fg='green')

    assertEquals(result["nnrtiCurrentAdults"], 38.1)
    assertEquals(result["nnrtiCurrentPaed"], 22.5)
    assertEquals(result["nnrtiNewAdults"], 32.5)
    assertEquals(result["nnrtiNewPaed"], 29.8)
