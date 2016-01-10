from collections import defaultdict

from django.test import TestCase
from mock import patch, call

from dashboard.data.tests.test_data import FakeReport
from dashboard.models import Score, CycleFormulationScore, Consumption, AdultPatientsRecord, PAEDPatientsRecord, Cycle
from dashboard.tasks import persist_scores, run_checks_and_persist_formulation_scores, persist_consumption, persist_adult_records, persist_paed_records, get_report_for_other_cycle, calculate_scores_for_checks_in_cycle


class TaskTestCase(TestCase):
    def test_should_create_scores_for_each_check(self):
        report = FakeReport()
        report.cs = defaultdict(list)
        report.ads = defaultdict(list)
        report.pds = defaultdict(list)
        report.cycle = "May - Jun 2015"
        report.locs = [{
            'name': 'location_one',
            'IP': 'ip_one',
            'District': 'district_one',
            'Warehouse': 'warehouse_one',
            'Multiple': '',
            'status': '',
            'Web/Paper': '',
            'scores': defaultdict(dict)
        }]
        self.assertEqual(CycleFormulationScore.objects.count(), 0)
        run_checks_and_persist_formulation_scores(report)
        run_checks_and_persist_formulation_scores(report)
        self.assertEqual(CycleFormulationScore.objects.count(), 32)

    def test_should_record_scores_for_each_facility(self):
        report = FakeReport()
        report.cycle = "May - Jun 2015"
        report.locs = [{
            'name': 'location_one',
            'IP': 'ip_one',
            'District': 'district_one',
            'Warehouse': 'warehouse_one',
            'scores': {
                'WEB_BASED': {'DEFAULT': 'YES'},
                'REPORTING': {'DEFAULT': 'NO'},
            }
        },
            {
                'name': 'location_two',
                'District': 'district_one',
                'IP': 'ip_one',
                'Warehouse': 'warehouse_one',
                'scores': {
                    'WEB_BASED': {'DEFAULT': 'YES'},
                    'REPORTING': {'DEFAULT': 'NO'},
                }
            }]
        self.assertEqual(Score.objects.count(), 0)
        persist_scores(report)
        persist_scores(report)
        self.assertEqual(Score.objects.count(), 2)
        first_score = Score.objects.all()[0]
        self.assertEqual(first_score.pass_count, 1)
        self.assertEqual(first_score.fail_count, 1)

    def test_should_record_consumption_for_each_facility(self):
        report = FakeReport()
        report.ads = defaultdict(list)
        report.pds = defaultdict(list)
        report.cycle = "May - Jun 2015"
        report.locs = [{
            'name': 'location_one',
            'IP': 'ip_one',
            'District': 'district_one',
            'Warehouse': 'warehouse_one',
            'Multiple': '',
            'status': '',
            'Web/Paper': '',
            'scores': defaultdict(dict)
        }]
        report.cs = {
            'location_one': [
                {
                    'opening_balance': 20,
                    'closing_balance': 12,
                }
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
        report.locs = [{
            'name': 'location_one',
            'IP': 'ip_one',
            'District': 'district_one',
            'Warehouse': 'warehouse_one',
            'Multiple': '',
            'status': '',
            'Web/Paper': '',
            'scores': defaultdict(dict)
        }]
        report.ads = {
            'location_one': [
                {
                    'new': 20,
                    'existing': 12,
                }
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
        report.locs = [{
            'name': 'location_one',
            'IP': 'ip_one',
            'District': 'district_one',
            'Warehouse': 'warehouse_one',
            'Multiple': '',
            'status': '',
            'Web/Paper': '',
            'scores': defaultdict(dict)
        }]
        report.pds = {
            'location_one': [
                {
                    'new': 20,
                    'existing': 12,
                }
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

    @patch('dashboard.tasks.run_checks_and_persist_formulation_scores')
    @patch('dashboard.tasks.persist_scores')
    @patch('dashboard.tasks.persist_consumption')
    @patch('dashboard.tasks.persist_adult_records')
    @patch('dashboard.tasks.persist_paed_records')
    def test_calculate_scores_for_checks_in_cycle(self, mock1, mock2, mock3, mock4, mock5):
        report = FakeReport()
        calculate_scores_for_checks_in_cycle(report)
        exepected_call = call(report)
        mock_methods = [mock1, mock2, mock3, mock4, mock5]
        for m in mock_methods:
            m.assert_has_calls([exepected_call])
