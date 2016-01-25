import djclick as click
from termcolor import colored

from dashboard.helpers import *
from dashboard.models import CycleFormulationScore, MultipleOrderFacility


@click.command()
def command():
    cycle = "May - Jun 2015"
    cycle2 = "Jul - Aug 2015"
    checks = [
        {'combination': DEFAULT, 'test': REPORTING, 'cycle': cycle, 'expected': 60.2},
        {'combination': DEFAULT, 'test': WEB_BASED, 'cycle': cycle, 'expected': 60.2},
        {'combination': DEFAULT, 'test': ORDER_FORM_FREE_OF_GAPS, 'cycle': cycle, 'expected': 31.9},
        {'combination': F1, 'test': ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, 'cycle': cycle, 'expected': 57.3},
        {'combination': F1, 'test': CONSUMPTION_AND_PATIENTS, 'cycle': cycle, 'expected': 18.7},
        {'combination': F1, 'test': DIFFERENT_ORDERS_OVER_TIME, 'cycle': cycle2, 'expected': 52.5},
        {'combination': F1, 'test': CLOSING_BALANCE_MATCHES_OPENING_BALANCE, 'cycle': cycle2, 'expected': 21.3},
        {'combination': F1, 'test': STABLE_CONSUMPTION, 'cycle': cycle2, 'expected': 29.3},
        {'combination': F1, 'test': WAREHOUSE_FULFILMENT, 'cycle': cycle2, 'expected': 29.1},
        {'combination': F1, 'test': STABLE_PATIENT_VOLUMES, 'cycle': cycle2, 'expected': 33.8},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_ADULT_1L, 'cycle': cycle, 'expected': 27.5},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_ADULT_2L, 'cycle': cycle, 'expected': 41.5},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_PAED_1L, 'cycle': cycle, 'expected': 26.8},
        {'combination': DEFAULT, 'test': NNRTI_CURRENT_ADULTS, 'cycle': cycle, 'expected': 38.1},
        {'combination': DEFAULT, 'test': NNRTI_NEW_ADULTS, 'cycle': cycle, 'expected': 32.5},
        {'combination': DEFAULT, 'test': NNRTI_CURRENT_PAED, 'cycle': cycle, 'expected': 22.5},
        {'combination': DEFAULT, 'test': NNRTI_NEW_PAED, 'cycle': cycle, 'expected': 29.8},
    ]

    for check in checks:
        score = CycleFormulationScore.objects.get(combination=check['combination'], test=check['test'], cycle=check['cycle'])
        expected = "{0:.1f}".format(check['expected'])
        actual = "{0:.1f}".format(score.yes)
        if expected == actual:
            print colored(check['test'] + " Passed", "green")
        else:
            c = "yellow" if abs(float(expected) - float(actual)) < 1 else "red"
            print colored(check['test'] + " Failed", c), colored("Got %s instead of %s " % (actual, expected), c)

    count = MultipleOrderFacility.objects.filter(cycle=cycle).count()
    expected = 33
    if count == expected:
        print colored(MULTIPLE_ORDERS + " Passed", "green")
    else:
        print colored(MULTIPLE_ORDERS + " Failed", 'red'), colored("Got %s instead of %s " % (count, expected), 'red')
