import os

from celery import shared_task

from dashboard.checks import run_order_form_free_of_gaps_test, run_order_form_free_of_negative_numbers_test
from dashboard.reports import GeneralReport


@shared_task
def calculate_scores_for_checks_in_cycle(cycle):
    run_order_form_free_of_gaps_test(cycle)
    run_order_form_free_of_negative_numbers_test(cycle)


@shared_task
def import_general_report(path, cycle):
    GeneralReport(path, cycle).get_data()
    os.remove(path)
    calculate_scores_for_checks_in_cycle.delay(cycle)
