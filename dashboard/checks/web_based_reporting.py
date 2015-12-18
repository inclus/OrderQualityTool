from dashboard.checks.common import CycleFormulationCheck
from dashboard.helpers import WEB_BASED, NO, YES, REPORTING, MULTIPLE_ORDERS
from dashboard.models import Cycle


class WebBasedReportingCheck(CycleFormulationCheck):
    test = WEB_BASED

    def run(self, cycle):
        for record in Cycle.objects.filter(cycle=cycle):
            result = YES if record.web_based else NO
            self.record_result_for_facility(record, result)


class ReportingCheck(CycleFormulationCheck):
    test = REPORTING

    def run(self, cycle):
        for record in Cycle.objects.filter(cycle=cycle):
            result = YES if record.reporting_status else NO
            self.record_result_for_facility(record, result)


class MultipleOrdersCheck(CycleFormulationCheck):
    test = MULTIPLE_ORDERS

    def run(self, cycle):
        for record in Cycle.objects.filter(cycle=cycle):
            result = YES if record.multiple else NO
            self.record_result_for_facility(record, result)
