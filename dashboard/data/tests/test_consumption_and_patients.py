from collections import defaultdict

from django.test import TestCase

from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.tests.test_data import FakeReport


class ConsumptionAndPatientsQualityCheckTestCase(TestCase):
    def test_report_can_search_for_record_by_subset(self):
        report = FakeReport()
        check = ConsumptionAndPatientsQualityCheck(report)
        collection = defaultdict(list)
        collection["The place name"] = [
            {
                "formulation": "F1"
            }
        ]
        facility_name = "The place"
        cycle = "Jul - Aug 2015"
        records = check.get_records_from_collection(collection, facility_name, cycle)
        self.assertEqual(records, [{'formulation': 'F1'}])

    def test_report_can_search_for_record(self):
        report = FakeReport()
        check = ConsumptionAndPatientsQualityCheck(report)
        collection = defaultdict(list)
        collection["The place"] = [
            {
                "formulation": "F1"
            }
        ]
        collection["The other place"] = [
            {
                "formulation": "F2"
            }
        ]
        facility_name = "The place name"
        cycle = "Jul - Aug 2015"
        records = check.get_records_from_collection(collection, facility_name, cycle)
        self.assertEqual(records, [{'formulation': 'F1'}])
