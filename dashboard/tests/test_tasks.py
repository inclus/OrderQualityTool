from collections import defaultdict

import os
from django.test import TestCase
from mock import patch

from dashboard.data.entities import Location, PatientRecord, ConsumptionRecord
from dashboard.data.tests.test_data import FakeReport
from dashboard.models import Score, Consumption, AdultPatientsRecord, PAEDPatientsRecord, Cycle, MultipleOrderFacility
from dashboard.data.tasks import persist_consumption, persist_adult_records, persist_paed_records, \
    persist_multiple_order_records, get_report_for_other_cycle, persist_scores
from dashboard.tasks import run_manual_import
from dashboard.views.main import serialize_upload_file


class TaskTestCase(TestCase):

    @patch('dashboard.tasks.update_checks.apply_async')
    def test_should_import_file(self, mocked):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures',
                                 "new_format.xlsx")
        with open(file_path, "rb") as file_handle:
            data = serialize_upload_file(file_handle)
            cycle = run_manual_import("May Jun", data)
            self.assertEqual( 1, cycle.id)

    def test_should_record_scores_for_each_facility(self):
        report = FakeReport()
        report.cycle = "May - Jun 2015"
        location_one = Location.migrate_from_dict(
            {'name': 'location_one', 'IP': 'ip_one', 'District': 'district_one', 'Warehouse': 'warehouse_one'})
        location_two = Location.migrate_from_dict(
            {'name': 'location_two', 'District': 'district_one', 'IP': 'ip_one', 'Warehouse': 'warehouse_one', })
        report.locs = [location_one, location_two]
        scores_cache = {
            location_one: {'WEB_BASED': {'DEFAULT': 'YES'}, 'REPORTING': {'DEFAULT': 'NO'}, },
            location_two: {'WEB_BASED': {'DEFAULT': 'YES'}, 'REPORTING': {'DEFAULT': 'NO'}, }, }

        self.assertEqual(Score.objects.count(), 0)
        persist_scores(scores_cache, report.cycle)
        persist_scores(scores_cache, report.cycle)
        self.assertEqual(Score.objects.count(), 2)
        first_score = Score.objects.all()[0]
        self.assertEqual(first_score.default_pass_count, 1)
        self.assertEqual(first_score.default_fail_count, 1)

    def test_should_record_consumption_for_each_facility(self):
        report = FakeReport()
        report.ads = defaultdict(list)
        report.pds = defaultdict(list)
        report.cycle = "May - Jun 2015"
        location = Location.migrate_from_dict(
            {'name': 'location_one', 'IP': 'ip_one', 'District': 'district_one', 'Warehouse': 'warehouse_one',
             'Multiple': '', 'status': '', 'Web/Paper': '', 'scores': defaultdict(dict)})
        report.locs = [location]
        report.cs = {
            location: [
                ConsumptionRecord.migrate_from_dict({
                    'opening_balance': 20,
                    'closing_balance': 12,
                })
            ]
        }
        self.assertEqual(Consumption.objects.count(), 0)
        persist_consumption(report)
        self.assertEqual(Consumption.objects.count(), 1)
        first_record = Consumption.objects.all()[0]
        self.assertEqual(first_record.name, 'location_one')
        self.assertEqual(first_record.ip, 'ip_one')
        self.assertEqual(first_record.district, 'district_one')
        self.assertEqual(first_record.warehouse, 'warehouse_one')
        self.assertEqual(first_record.opening_balance, 20)
        self.assertEqual(first_record.closing_balance, 12)

    def test_should_record_adult_records_for_each_facility(self):
        report = FakeReport()
        report.ads = defaultdict(list)
        report.pds = defaultdict(list)
        report.cycle = "May - Jun 2015"
        location = Location.migrate_from_dict(
            {'name': 'location_one', 'IP': 'ip_one', 'District': 'district_one', 'Warehouse': 'warehouse_one',
             'Multiple': '', 'status': '', 'Web/Paper': '', 'scores': defaultdict(dict)})
        report.locs = [location]
        report.ads = {
            location: [
                PatientRecord.migrate_from_dict({
                    'new': 20,
                    'existing': 12,
                })
            ]
        }
        self.assertEqual(AdultPatientsRecord.objects.count(), 0)
        persist_adult_records(report)
        self.assertEqual(AdultPatientsRecord.objects.count(), 1)
        first_record = AdultPatientsRecord.objects.all()[0]
        self.assertEqual(first_record.name, 'location_one')
        self.assertEqual(first_record.ip, 'ip_one')
        self.assertEqual(first_record.district, 'district_one')
        self.assertEqual(first_record.warehouse, 'warehouse_one')
        self.assertEqual(first_record.new, 20)
        self.assertEqual(first_record.existing, 12)

    def test_should_record_paed_records_for_each_facility(self):
        report = FakeReport()
        report.ads = defaultdict(list)
        report.pds = defaultdict(list)
        report.cycle = "May - Jun 2015"
        location_one = Location.migrate_from_dict(
            {'name': 'location_one', 'IP': 'ip_one', 'District': 'district_one', 'Warehouse': 'warehouse_one',
             'Multiple': '', 'status': '', 'Web/Paper': '', 'scores': defaultdict(dict)})
        report.locs = [location_one]
        report.pds = {
            location_one: [
                PatientRecord.migrate_from_dict({
                    'new': 20,
                    'existing': 12,
                })
            ]
        }
        self.assertEqual(PAEDPatientsRecord.objects.count(), 0)
        persist_paed_records(report)
        self.assertEqual(PAEDPatientsRecord.objects.count(), 1)
        first_record = PAEDPatientsRecord.objects.all()[0]
        self.assertEqual(first_record.name, 'location_one')
        self.assertEqual(first_record.ip, 'ip_one')
        self.assertEqual(first_record.district, 'district_one')
        self.assertEqual(first_record.warehouse, 'warehouse_one')
        self.assertEqual(first_record.new, 20)
        self.assertEqual(first_record.existing, 12)

    def test_get_report_for_other_cycle(self):
        state = {'cs': [1, 2]}
        Cycle.objects.create(title="May - Jun 2015", state=state)
        report = FakeReport()
        report.cycle = 'Jul - Aug 2015'
        other_report = get_report_for_other_cycle(report)
        self.assertEqual(other_report.cs, [1, 2])

    # @patch('dashboard.tasks.run_checks')
    # @patch('dashboard.tasks.persist_scores')
    # @patch('dashboard.tasks.persist_consumption')
    # @patch('dashboard.tasks.persist_adult_records')
    # @patch('dashboard.tasks.persist_paed_records')
    # @patch('dashboard.tasks.persist_multiple_order_records')
    # def test_calculate_scores_for_checks_in_cycle(self, mock1, mock2, mock3, mock4, mock5, mock_run_checks):
    #     report = FakeReport()
    #     report.cycle = "May - Jun 2015"
    #     calculate_scores_for_checks_in_cycle(report)
    #     exepected_call = call(report)
    #     mock_methods = [mock1, mock2, mock3, mock4, mock5, mock_run_checks]
    #     for m in mock_methods:
    #         m.assert_has_calls([exepected_call])

    def test_should_record_facilities_with_multiple_orders(self):
        report = FakeReport()
        report.ads = defaultdict(list)
        report.pds = defaultdict(list)
        report.cycle = "May - Jun 2015"
        two = Location(facility="location_two", district="district_one", warehouse="warehouse_one",
                       partner="ip_one", multiple="Multiple orders")
        one = Location(facility="location_one", district="district_one", warehouse="warehouse_one",
                       partner="ip_one")
        report.locs = [
            one,
            two
        ]
        self.assertEqual(MultipleOrderFacility.objects.count(), 0)
        persist_multiple_order_records(report)
        self.assertEqual(MultipleOrderFacility.objects.count(), 1)
