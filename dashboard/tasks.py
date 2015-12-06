import os

from celery import shared_task

from dashboard.checks.order_form_free_of_gaps import OrderFormFreeOfGaps
from dashboard.checks.order_free_of_negative_numbers import OrderFormFreeOfNegativeNumbers
from dashboard.reports import GeneralReport


@shared_task
def calculate_scores_for_checks_in_cycle(cycle):
    OrderFormFreeOfGaps().run(cycle)
    OrderFormFreeOfNegativeNumbers().run(cycle)


@shared_task
def import_general_report(path, cycle):
    GeneralReport(path, cycle).get_data()
    os.remove(path)
    calculate_scores_for_checks_in_cycle.delay(cycle)
