from django.test import TestCase

from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.utils import get_patient_records
from dashboard.helpers import *


class ConsumptionAndPatientsQualityCheckTestCase(TestCase):
    def test_get_patient_records(self):
        data = {
            A_RECORDS: [
                {FORMULATION: 'A', NEW: 1},
                {FORMULATION: 'B', NEW: 2},
                {FORMULATION: 'C', NEW: 3}
            ]
        }

        check = ConsumptionAndPatientsQualityCheck()
        records = get_patient_records(data, ["A", "B"], True)
        self.assertEqual(records, [{'formulation': 'A', 'new': 1}, {'formulation': 'B', 'new': 2}])
