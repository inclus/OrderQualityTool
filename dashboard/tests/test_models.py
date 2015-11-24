import os

from django.test import TestCase

from dashboard.models import WaosStandardReport, FacilityConsumptionRecord, GeneralReport
from locations.models import Location


class WaosStandardReportTestCase(TestCase):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path

    def test_can_get_record_from_file(self):
        Location.objects.get_or_create(name="AIC Jinja Special Clinic", uid="AIC Jinja", level=1)
        record = WaosStandardReport(self.get_fixture_path('b.xls')).get_facility_record()
        self.assertEqual(record.cycle, "Jul-Aug 2015")
        self.assertEqual(record.facility.name, "AIC Jinja Special Clinic")

    def test_can_build_consumption_records_from_file(self):
        Location.objects.get_or_create(name="AIC Jinja Special Clinic", uid="AIC Jinja Special Clinic", level=1)
        WaosStandardReport(self.get_fixture_path('b.xls')).get_data()
        self.assertEqual(FacilityConsumptionRecord.objects.count(), 18)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).opening_balance, 105)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).closing_balance, 381)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).months_of_stock_of_hand, 3.1)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).total_quantity_to_be_ordered, 131)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=11).opening_balance, None)


class GeneralReportTestCase(TestCase):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path

    def test_import_is_efficient(self):
        Location.objects.get_or_create(name="Bugaya HC III ( Buvuma )", uid="1234", level=1)
        with self.assertNumQueries(7):
            GeneralReport(self.get_fixture_path('new_format_small.xlsx'), "Jan- Feb 2000").consumption_records()
        self.assertEqual(FacilityConsumptionRecord.objects.count(), 13)

    def test_can_build_consumption_records_from_file(self):
        Location.objects.get_or_create(name="Bugaya HC III ( Buvuma )", uid="1234", level=1)
        Location.objects.get_or_create(name="Gulu Regional Referal Hospital", uid="234", level=1)
        GeneralReport(self.get_fixture_path('new_format.xlsx'), "Jan- Feb 2000").get_data()
        self.assertEqual(FacilityConsumptionRecord.objects.count(), 41)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).opening_balance, 20)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).closing_balance, 18)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).months_of_stock_of_hand, 18)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).packs_ordered, -14)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=2).opening_balance, 35)
