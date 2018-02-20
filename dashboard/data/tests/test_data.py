import os
from collections import defaultdict

import responses
from django.contrib.admin.models import LogEntry
from django.test import TestCase

from dashboard.checks.legacy.adherence import GuidelineAdherenceCheckAdult1L, calculate_score
from dashboard.checks.legacy.blanks import BlanksQualityCheck, IsReportingCheck, MultipleCheck
from dashboard.data.data_import import ExcelDataImport
from dashboard.data.entities import enrich_location_data, LocationData, PatientRecord
from dashboard.data.html_data_import import HtmlDataImport
from dashboard.data.tests.test_html_data_import import get_test_output_from_fixture
from dashboard.checks.legacy.check import values_for_records, get_consumption_totals, get_patient_total, \
    get_consumption_records, get_patient_records
from dashboard.helpers import *
from dashboard.medist.tests.test_helpers import fake_orgunit_response
from dashboard.models import Score, Consumption, PAEDPatientsRecord, AdultPatientsRecord, MultipleOrderFacility, \
    LocationToPartnerMapping
from dashboard.tasks import calculate_scores_for_checks_in_cycle


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
        data = LocationData.migrate_from_dict({C_RECORDS: [{FORMULATION: "A", OPENING_BALANCE: 3},
                                                           {FORMULATION: "B", OPENING_BALANCE: 3},
                                                           {FORMULATION: "A", OPENING_BALANCE: 12}]})

        records = get_consumption_records(data, "A")
        self.assertEqual(records[0].formulation, "A")
        self.assertEqual(records[0].opening_balance, 3)
        self.assertEqual(records[1].formulation, "A")
        self.assertEqual(records[1].opening_balance, 12)

    def test_adult_records(self):
        data = LocationData.migrate_from_dict({
            A_RECORDS: [
                {FORMULATION: "A", NEW: 3},
                {FORMULATION: "B", NEW: 3},
                {FORMULATION: "A", NEW: 12}]

        })
        records = get_patient_records(data, "A", True)
        self.assertEqual(records[0].formulation, "A")
        self.assertEqual(records[0].new, 3)
        self.assertEqual(records[1].formulation, "A")
        self.assertEqual(records[1].new, 12)

    def test_patient_totals(self):
        assert get_patient_total([
            PatientRecord.migrate_from_dict({NEW: 10, EXISTING: 12}),
            PatientRecord.migrate_from_dict({NEW: None, EXISTING: 12})]) == 34

    def test_consumption_totals(self):
        assert get_consumption_totals([NEW], [
            PatientRecord.migrate_from_dict({NEW: 10, EXISTING: 12}),
            PatientRecord.migrate_from_dict({NEW: None, EXISTING: 12})]) == 10
        assert get_consumption_totals([NEW], [
            PatientRecord.migrate_from_dict({NEW: None, EXISTING: 12}),
            PatientRecord.migrate_from_dict({NEW: 10, EXISTING: 12})]) == 10
        assert get_consumption_totals([EXISTING], [
            PatientRecord.migrate_from_dict({NEW: 10, EXISTING: 12}),
            PatientRecord.migrate_from_dict({NEW: None, EXISTING: 12})]) == 24
        assert get_consumption_totals([EXISTING, NEW],
                                      [
                                          PatientRecord.migrate_from_dict({NEW: 10, EXISTING: 12}),
                                          PatientRecord.migrate_from_dict({NEW: None, EXISTING: 12})]) == 34

    def test_values_for_records(self):
        assert values_for_records([NEW], [
            PatientRecord.migrate_from_dict({NEW: 10, EXISTING: 12}),
            PatientRecord.migrate_from_dict({NEW: None, EXISTING: 12})]) == [10, None]

    def test_blanks(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'fixtures',
                                 "new_format.xlsx")
        report = ExcelDataImport(file_path, "May Jun").load()
        report.cycle = "Jul - Aug 2015"
        cases = [
            {'test': BlanksQualityCheck, 'expected': NOT_REPORTING},
            {'test': MultipleCheck, 'expected': YES},
            {'test': IsReportingCheck, 'expected': YES},
        ]
        for case in cases:
            check = case['test']()
            scores = defaultdict(lambda: defaultdict(dict))
            for combination in check.combinations:
                facility_data = enrich_location_data(report.locs[0], report)
                scores[check.test][combination[NAME]] = check.for_each_facility(
                    facility_data, combination)
            self.assertEquals(scores[case['test'].test][DEFAULT], case['expected'])

    def test_full_excel_import(self):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'fixtures',
                                 "new_format.xlsx")
        report = ExcelDataImport(file_path, "May Jun").load()
        test_cycle = "Jul - Aug 2015"
        report.cycle = test_cycle
        self.assertEqual(len(report.locs), 24)
        calculate_scores_for_checks_in_cycle(report)
        self.assertEqual(len(Score.objects.filter(cycle=test_cycle)), 24)
        self.assertEqual(len(AdultPatientsRecord.objects.filter(cycle=test_cycle)), 44)
        self.assertEqual(len(PAEDPatientsRecord.objects.filter(cycle=test_cycle)), 28)
        self.assertEqual(len(Consumption.objects.filter(cycle=test_cycle)), 41)
        self.assertEqual(len(MultipleOrderFacility.objects.filter(cycle=test_cycle)), 5)
        entries = LogEntry.objects.all()
        self.assertEqual(len(entries), 1)

    @responses.activate
    @fake_orgunit_response()
    def test_full_html_import(self):
        fixture = get_test_output_from_fixture("arv-0-consumption-data-report-maul.html",
                                               report_type=CONSUMPTION_REPORT)
        fixture.extend(get_test_output_from_fixture("arv-0-consumption-data-report-maul.html",
                                                    report_type=CONSUMPTION_REPORT))
        report = HtmlDataImport(fixture, "May Jun").load(LocationToPartnerMapping.get_mapping())
        test_cycle = "Jul - Aug 2015"
        report.cycle = test_cycle
        self.assertEqual(len(report.locs), 50)
        entries = LogEntry.objects.all()
        self.assertEqual(len(entries), 0)

        calculate_scores_for_checks_in_cycle(report)
        self.assertEqual(len(Score.objects.filter(cycle=test_cycle)), 50)
        self.assertEqual(len(AdultPatientsRecord.objects.filter(cycle=test_cycle)), 0)
        self.assertEqual(len(PAEDPatientsRecord.objects.filter(cycle=test_cycle)), 0)
        self.assertEqual(len(Consumption.objects.filter(cycle=test_cycle)), 0)
        self.assertEqual(len(MultipleOrderFacility.objects.filter(cycle=test_cycle)), 0)
        entries = LogEntry.objects.all()
        self.assertEqual(len(entries), 1)


class GuidelineAdherenceAdult1LTestCase(TestCase):
    def test_score_is_yes_if_sum_of_new_hiv_positive_women_and_new_art_for_tdf_is_80_percent_that_for_AZT(self):
        df1_count = df2_count = 1
        sum_df1 = 9
        sum_df2 = 2
        ratio = 0.8
        result = calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio)
        self.assertEqual(result, YES)

    def test_score_is_yes_if_sum_of_new_hiv_positive_women_and_new_art_for_tdf_is_zero_and_that_for_AZT_is_also_zero(
            self):
        df1_count = df2_count = 1
        sum_df1 = 0
        sum_df2 = 0
        ratio = 0.8
        result = calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio)
        self.assertEqual(result, YES)

    def test_score_is_no_if_tdf_cells_are_blank(self):
        df1_count = df2_count = 1
        sum_df1 = 0
        sum_df2 = 12
        ratio = 0.8
        result = calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, True,
                                 False)
        self.assertEqual(result, NO)

    def test_score_is_no_if_azt_cells_are_blank(self):
        df1_count = df2_count = 1
        sum_df1 = 0
        sum_df2 = 20
        ratio = 0.8
        result = calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, False,
                                 True)
        self.assertEqual(result, NO)

    def test_score_is_not_reporting_if_azt_or_tdf_cells_are_not_found(self):
        df1_count = df2_count = 0
        sum_df1 = 0
        sum_df2 = 0
        ratio = 0.8
        result = calculate_score(df1_count, df2_count, sum_df1, sum_df2, ratio, False,
                                 True)
        self.assertEqual(result, NOT_REPORTING)

    def test_adherence_filter(self):
        data = LocationData.migrate_from_dict({
            C_RECORDS: [
                {
                    FORMULATION: "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]",
                    "estimated_number_of_new_pregnant_women": 9,
                    "estimated_number_of_new_patients": 9
                },
                {
                    FORMULATION: "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]",
                    "estimated_number_of_new_pregnant_women": 9,
                    "estimated_number_of_new_patients": 9
                },
                {
                    FORMULATION: "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]",
                    "estimated_number_of_new_pregnant_women": 1,
                    "estimated_number_of_new_patients": 1
                },
                {
                    FORMULATION: "Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 300mg/150mg/200mg [Pack 60]",
                    "estimated_number_of_new_pregnant_women": 1,
                    "estimated_number_of_new_patients": 1
                },
                {FORMULATION: "A", "openingBalance": 12}],
            STATUS: REPORTING
        })
        check = GuidelineAdherenceCheckAdult1L()
        result = check.for_each_facility(data, check.combinations[0])
        self.assertEqual(result, YES)


def clean_name(row):
    full_name = row[0].value
    replace_template = "_" + row[5].value.strip()
    return full_name.strip().replace(replace_template, "")