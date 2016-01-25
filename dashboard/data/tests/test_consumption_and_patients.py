from collections import defaultdict

from django.test import TestCase

from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.tests.test_data import FakeReport


class ConsumptionAndPatientsQualityCheckTestCase(TestCase):
    def test_report_can_search_for_record_by_subset(self):
        report = FakeReport()
        check = ConsumptionAndPatientsQualityCheck(report)
        collection = defaultdict(list)
        collection["The place"] = [
            {
                "formulation": "F1"
            }
        ]
        facility_name = "The place"
        records = check.get_records_from_collection(collection, facility_name)
        self.assertEqual(records, [{'formulation': 'F1'}])
