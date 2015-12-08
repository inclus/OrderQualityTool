import os

from celery import shared_task

from dashboard.checks.closing_balance import ClosingBalance
from dashboard.checks.consumption_and_patients import ConsumptionAndPatients
from dashboard.checks.different_orders_over_time import DifferentOrdersOverTime
from dashboard.checks.order_form_free_of_gaps import OrderFormFreeOfGaps
from dashboard.checks.order_free_of_negative_numbers import OrderFormFreeOfNegativeNumbers
from dashboard.checks.stable_consumption import StableConsumption
from dashboard.reports import GeneralReport


@shared_task
def process_test(check_class, cycle):
    return check_class().run(cycle)


@shared_task
def calculate_scores_for_checks_in_cycle(cycle):
    process_test.delay(OrderFormFreeOfGaps, cycle)
    process_test.delay(OrderFormFreeOfNegativeNumbers, cycle)
    process_test.delay(DifferentOrdersOverTime, cycle)
    process_test.delay(ClosingBalance, cycle)
    process_test.delay(ConsumptionAndPatients, cycle)
    process_test.delay(StableConsumption, cycle)


@shared_task
def import_general_report(path, cycle):
    GeneralReport(path, cycle).get_data()
    os.remove(path)
    calculate_scores_for_checks_in_cycle.delay(cycle)
