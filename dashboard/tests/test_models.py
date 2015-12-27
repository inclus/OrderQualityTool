import os

from django.test import TestCase

from dashboard.models import Consumption, Cycle
from dashboard.reports import GeneralReport
from locations.models import Facility


class FixtureFileReportTestCase(TestCase):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path


class GeneralReportTestCase(FixtureFileReportTestCase):
    def test_should_import_locations(self):
        GeneralReport(self.get_fixture_path('new_format_small.xlsx'), "Jan- Feb 2000").locations()
        self.assertEqual(Facility.objects.count(), 25)
        self.assertEqual(Cycle.objects.count(), 25)

    def test_import_is_efficient(self):
        Facility.objects.get_or_create(name="Bugaya HC III ( Buvuma )")
        with self.assertNumQueries(7):
            GeneralReport(self.get_fixture_path('new_format_small.xlsx'), "Jan- Feb 2000").consumption_records()
        self.assertEqual(Consumption.objects.count(), 13)

    def test_can_build_consumption_records_from_file(self):
        GeneralReport(self.get_fixture_path('new_format.xlsx'), "Jan- Feb 2000").get_data()
        self.assertEqual(Consumption.objects.count(), 41)
        first_record = Consumption.objects.get(formulation="Cotrimoxazole 120mg [Pack 1000]", facility_cycle__facility__name="Bugaya HC III ( Buvuma )")
        second_record = Consumption.objects.get(formulation="Cotrimoxazole 960mg[Pack 1000]", facility_cycle__facility__name="Bugaya HC III ( Buvuma )")
        self.assertEqual(first_record.opening_balance, 20)
        self.assertEqual(first_record.closing_balance, 18)
        self.assertEqual(first_record.months_of_stock_of_hand, 18)
        self.assertEqual(first_record.packs_ordered, -14)
        self.assertEqual(second_record.opening_balance, 35)
        GeneralReport(self.get_fixture_path('new_format_changed.xlsx'), "Jan- Feb 2012").get_data()
        self.assertEqual(Consumption.objects.count(), 82)
