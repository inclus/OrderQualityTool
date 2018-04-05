from collections import defaultdict

import pygogo

from dashboard.checks.entities import Definition
from dashboard.checks.legacy.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckAdult2L, \
    GuidelineAdherenceCheckPaed1L
from dashboard.checks.legacy.blanks import BlanksQualityCheck, MultipleCheck, IsReportingCheck
from dashboard.checks.legacy.volumetally import VolumeTallyCheck
from dashboard.checks.legacy.cycles import BalancesMatchCheck, OrdersOverTimeCheck, StableConsumptionCheck, \
    WarehouseFulfillmentCheck, StablePatientVolumesCheck
from dashboard.checks.legacy.negatives import NegativeNumbersQualityCheck
from dashboard.checks.legacy.nn import NNRTIADULTSCheck, NNRTIPAEDCheck
from dashboard.checks.check import get_check
from dashboard.data.entities import enrich_location_data
from dashboard.data.tasks import get_report_for_other_cycle
from dashboard.helpers import NAME
from dashboard.models import FacilityTest
from dashboard.utils import timeit, log_formatter
from raven.contrib.django.raven_compat.models import client

logger = pygogo.Gogo(__name__, low_formatter=log_formatter).get_logger()


@timeit
def run_dynamic_checks(report):
    scores = defaultdict(lambda: defaultdict(dict))
    other_report = get_report_for_other_cycle(report)
    facility_tests = FacilityTest.objects.all()
    for check_obj in facility_tests:
        # try:
        run_facility_test(check_obj, report, other_report, scores)
    # except Exception as e:
    #     logger.info("error running tests", extra={"error": e.message, "check": check_obj.name})
    #     client.captureException()
    return scores


def run_facility_test(check_obj, report, other_report, scores):
    definition = Definition.from_string(check_obj.definition)
    check_to_run = get_check(definition)
    if check_to_run:
        for location in report.locs:
            facility_data = enrich_location_data(location, report)
            other_facility_data = enrich_location_data(location, other_report)
            for combination in check_to_run.get_combinations():
                scores[location][check_obj.name][combination.key] = check_to_run.for_each_facility(
                    facility_data,
                    combination,
                    other_facility_data)


@timeit
def run_checks(report):
    scores = defaultdict(lambda: defaultdict(dict))
    other_report = get_report_for_other_cycle(report)
    checks = [
        BlanksQualityCheck(),
        NegativeNumbersQualityCheck(),
        VolumeTallyCheck(),
        MultipleCheck(),
        IsReportingCheck(),
        GuidelineAdherenceCheckAdult1L(),
        GuidelineAdherenceCheckAdult2L(),
        GuidelineAdherenceCheckPaed1L(),
        NNRTIADULTSCheck(),
        NNRTIPAEDCheck(),
        BalancesMatchCheck(),
        OrdersOverTimeCheck(),
        StableConsumptionCheck(),
        WarehouseFulfillmentCheck(),
        StablePatientVolumesCheck()
    ]
    for location in report.locs:
        facility_data = enrich_location_data(location, report)
        other_facility_data = enrich_location_data(location, other_report)
        for check in checks:
            for combination in check.combinations:
                scores[location][check.test][combination[NAME]] = check.for_each_facility(facility_data,
                                                                                          combination,
                                                                                          other_facility_data)
    return scores
