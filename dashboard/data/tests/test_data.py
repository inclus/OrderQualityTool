import os
from unittest import TestCase

from dashboard.data.blanks import BlanksQualityCheck
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.free_form_report import FreeFormReport
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.data.utils import clean_name, FORMULATION, NEW, get_patient_total, EXISTING, get_consumption_totals, \
    values_for_records


class FakeReport():
    pass


class Cell():
    def __init__(self, value):
        self.value = value


class DataTestCase(TestCase):
    def test_clean_name(self):
        row = [Cell("Byakabanda HC III_Rakai"), Cell(""), Cell(""), Cell(""), Cell(""), Cell("Rakai ")]
        assert clean_name(row) == "Byakabanda HC III"

    def test_consumption_records(self):
        report = FakeReport()
        report.cs = {"PLACE1": [{FORMULATION: "A", "openingBalance": 3},
                                {FORMULATION: "B", "openingBalance": 3},
                                {FORMULATION: "A", "openingBalance": 12}]}
        check = ConsumptionAndPatientsQualityCheck(report)
        records = check.get_consumption_records("PLACE1", "A")
        assert records == [{FORMULATION: "A", "openingBalance": 3}, {FORMULATION: "A", "openingBalance": 12}]

    def test_patient_records(self):
        report = FakeReport()
        report.pds = {"PLACE1": [{FORMULATION: "A1", NEW: 3},
                                 {FORMULATION: "B", NEW: 3},
                                 {FORMULATION: "A2", NEW: 12}]}
        check = ConsumptionAndPatientsQualityCheck(report)
        records = check.get_patient_records("PLACE1", "A", False)
        assert records == [{FORMULATION: "A1", NEW: 3}, {FORMULATION: "A2", NEW: 12}]

    def test_adult_records(self):
        report = FakeReport()
        report.ads = {"PLACE1": [{FORMULATION: "A", NEW: 3},
                                 {FORMULATION: "B", NEW: 3},
                                 {FORMULATION: "A", NEW: 12}]}
        check = ConsumptionAndPatientsQualityCheck(report)
        records = check.get_patient_records("PLACE1", "A", True)
        assert records == [{FORMULATION: "A", NEW: 3}, {FORMULATION: "A", NEW: 12}]

    def test_patient_totals(self):
        assert get_patient_total([{NEW: 10, EXISTING: 12}, {NEW: None, EXISTING: 12}]) == 34

    def test_consumption_totals(self):
        assert get_consumption_totals([NEW], [{NEW: 10, EXISTING: 12}, {NEW: None, EXISTING: 12}]) == 10
        assert get_consumption_totals([NEW], [{NEW: None, EXISTING: 12}, {NEW: 10, EXISTING: 12}]) == 10
        assert get_consumption_totals([EXISTING], [{NEW: 10, EXISTING: 12}, {NEW: None, EXISTING: 12}]) == 24
        assert get_consumption_totals([EXISTING, NEW],
                                      [{NEW: 10, EXISTING: 12}, {NEW: None, EXISTING: 12}]) == 34

    def test_values_for_records(self):
        assert values_for_records([NEW], [{NEW: 10, EXISTING: 12}, {NEW: None, EXISTING: 12}]) == [10, None]

    def test_blanks(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'fixtures',
                                 "new_format.xlsx")
        report = FreeFormReport(file_path, "May Jun").load()
        no, not_reporting, yes = BlanksQualityCheck(report).run()['DEFAULT']
        assert yes == 8.0

    def x_test_calculate_score(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'fixtures',
                                 "new_format.xlsx")
        report = FreeFormReport(file_path, "May Jun").load()
        no, not_reporting, yes = NegativeNumbersQualityCheck(report).run()['DEFAULT']
        assert yes == 57.3
