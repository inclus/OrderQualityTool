import os
import time

from celery import shared_task

from dashboard.checks.closing_balance import ClosingBalance
from dashboard.checks.consumption_and_patients import ConsumptionAndPatients
from dashboard.checks.different_orders_over_time import DifferentOrdersOverTime
from dashboard.checks.guideline_adherence import GuidelineAdherence
from dashboard.checks.nnrti_checks import NNRTI
from dashboard.checks.order_form_free_of_gaps import OrderFormFreeOfGaps
from dashboard.checks.order_free_of_negative_numbers import OrderFormFreeOfNegativeNumbers
from dashboard.checks.stable_consumption import StableConsumption
from dashboard.checks.stable_patient_volumes import StablePatientVolumes
from dashboard.checks.warehouse_fulfilement import WarehouseFulfilment
from dashboard.checks.web_based_reporting import WebBasedReportingCheck, ReportingCheck, MultipleOrdersCheck
from dashboard.reports import GeneralReport


@shared_task
def process_test(check_class, cycle):
    start_time = time.clock()
    result = check_class().run(cycle)
    print ("TIMER =================> ", check_class.__name__, time.clock() - start_time, "seconds")
    return result


@shared_task
def calculate_scores_for_checks_in_cycle(cycle):
    process_test(WebBasedReportingCheck, cycle)
    process_test(ReportingCheck, cycle)
    process_test(MultipleOrdersCheck, cycle)
    process_test(OrderFormFreeOfGaps, cycle)
    process_test(OrderFormFreeOfNegativeNumbers, cycle)
    process_test(DifferentOrdersOverTime, cycle)
    process_test(ClosingBalance, cycle)
    process_test(ConsumptionAndPatients, cycle)
    process_test(StableConsumption, cycle)
    process_test(WarehouseFulfilment, cycle)
    process_test(StablePatientVolumes, cycle)
    process_test(GuidelineAdherence, cycle)
    process_test(NNRTI, cycle)


@shared_task
def import_general_report(path, cycle):
    GeneralReport(path, cycle).get_data()
    os.remove(path)
    calculate_scores_for_checks_in_cycle.delay(cycle)
