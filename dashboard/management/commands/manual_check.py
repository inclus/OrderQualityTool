import csv
import json

import djclick as click
from termcolor import colored

from dashboard.data.data_import import ExcelDataImport
from dashboard.helpers import *
from dashboard.models import Score, Cycle
from dashboard.checks.tasks import run_dynamic_checks
from dashboard.data.tasks import persist_scores


def make_cond(cond):
    cond = json.dumps(cond)[1:-1]  # remove '{' and '}'
    return (cond).replace(": ", ":")  # avoid '\"'


@click.command()
def command():
    perform_checks()


def export_results():
    cycles = ["Sep - Oct 2015"]
    cycle = cycle2 = cycles[0]
    checks = [
        {'combination': DEFAULT, 'test': ORDER_FORM_FREE_OF_GAPS, 'cycle': cycle},
        {'combination': F3, 'test': ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, 'cycle': cycle},
        {'combination': F3, 'test': CONSUMPTION_AND_PATIENTS, 'cycle': cycle},
        {'combination': F3, 'test': DIFFERENT_ORDERS_OVER_TIME, 'cycle': cycle2},
        {'combination': F3, 'test': STABLE_CONSUMPTION, 'cycle': cycle2},
        {'combination': F3, 'test': WAREHOUSE_FULFILMENT, 'cycle': cycle2},
        {'combination': F3, 'test': CLOSING_BALANCE_MATCHES_OPENING_BALANCE, 'cycle': cycle2},
        {'combination': F3, 'test': STABLE_PATIENT_VOLUMES, 'cycle': cycle2},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_ADULT_1L, 'cycle': cycle},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_ADULT_2L, 'cycle': cycle},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_PAED_1L, 'cycle': cycle},

    ]
    results = []
    for cycle in cycles:

        for test in checks:

            if test.get('combination') == DEFAULT:
                yes_condition = {DEFAULT: YES}
                no_condition = {DEFAULT: NO}
                not_reporting_condition = {(DEFAULT): NOT_REPORTING}
                data = {"cycle": cycle, "test": test.get('test'), 'formulation': test.get('combination')}
                for key, condition in {YES: yes_condition, NO: no_condition,
                                       NOT_REPORTING: not_reporting_condition}.items():
                    filter_key = "%s__icontains" % test.get('test')
                    filter_by = {filter_key: make_cond(condition)}
                    count = Score.objects.filter(cycle=cycle, **filter_by).count()
                    data[key] = count
                results.append(data)
            else:
                for combination in [F1]:
                    yes_condition = {combination: YES}
                    no_condition = {combination: NO}
                    not_reporting_condition = {combination: NOT_REPORTING}
                    data = {"cycle": cycle, "test": test.get('test'), 'formulation': combination}
                    for key, condition in {YES: yes_condition, NO: no_condition,
                                           NOT_REPORTING: not_reporting_condition}.items():
                        filter_key = "%s__icontains" % test.get('test')
                        filter_by = {filter_key: make_cond(condition)}
                        count = Score.objects.filter(cycle=cycle, **filter_by).count()
                        data[key] = count
                    results.append(data)

    with open('out.csv', 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, ["test", "formulation", "cycle", "YES", "NO", "NOT_REPORTING"])
        w.writeheader()
        for item in results:
            w.writerow(item)
    return results


def perform_checks():
    cycle = "Sep - Oct 2015"
    data = Cycle.objects.filter(title=cycle)
    for cycle in data:
        report = ExcelDataImport(None, cycle.title).build_form_db(cycle)
        run_dynamic_checks(report)
        persist_scores(report)

    checks = [
        {'combination': F1, 'test': STABLE_PATIENT_VOLUMES, 'cycle': cycle, YES: 793, NO: 405, NOT_REPORTING: 632},
        {'combination': DEFAULT, 'test': NNRTI_PAED, 'cycle': cycle, YES: 548, NO: 780, NOT_REPORTING: 506},
        {'combination': DEFAULT, 'test': NNRTI_ADULTS, 'cycle': cycle, YES: 937, NO: 439, NOT_REPORTING: 458},
    ]
    for check in checks:
        if check.get('combination') == DEFAULT:
            yes_condition = {DEFAULT: YES}
            no_condition = {DEFAULT: NO}
            not_reporting_condition = {(DEFAULT): NOT_REPORTING}
        else:
            yes_condition = {check.get('combination'): YES}
            no_condition = {check.get('combination'): NO}
            not_reporting_condition = {check.get('combination'): NOT_REPORTING}
        for key, condition in {YES: yes_condition, NO: no_condition, NOT_REPORTING: not_reporting_condition}.items():
            test_description = "%s %s" % (check['test'], key)
            filter_key = "%s__icontains" % check.get('test')
            filter_by = {filter_key: make_cond(condition)}
            count = Score.objects.filter(cycle=check['cycle'], **filter_by).count()
            expected = check[key]
            actual = count
            if expected == actual:
                print
                colored(test_description + " Passed", "green")
            else:
                tolerance = 10
                diff = abs(float(expected) - float(actual))
                c = "yellow" if diff <= tolerance else "red"
                print
                colored(test_description + " Failed", c), colored("Got %s instead of %s " % (actual, expected),
                                                                  c), colored("diff: %s" % diff, "blue")
        print
        "\n"
