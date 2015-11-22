import os

from celery import shared_task

from dashboard.models import GeneralReport


@shared_task
def import_general_report(path, cycle):
    GeneralReport(path, cycle).get_data()
    os.remove(path)
