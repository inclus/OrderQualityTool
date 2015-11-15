import os

from django.test import TestCase

from dashboard.models import WaosFile, FacilityConsumptionRecord
from locations.models import Location


class WaosFileTestCase(TestCase):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path

    def test_can_get_record_from_file(self):
        Location.objects.get_or_create(name="AIC Jinja Special Clinic", uid="AIC Jinja", level=1)
        record = WaosFile(self.get_fixture_path('b.xls')).get_facility_record()
        self.assertEqual(record.cycle, "Jul-Aug 2015")
        self.assertEqual(record.facility.name, "AIC Jinja Special Clinic")

    def test_can_build_consumption_records_from_file(self):
        Location.objects.get_or_create(name="AIC Jinja Special Clinic", uid="AIC Jinja Special Clinic", level=1)
        WaosFile(self.get_fixture_path('b.xls')).get_data()
        self.assertEqual(FacilityConsumptionRecord.objects.count(), 18)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).opening_balance, 105)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).closing_balance, 381)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).months_of_stock_of_hand, 3.1)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=1).total_quantity_to_be_ordered, 131)
        self.assertEqual(FacilityConsumptionRecord.objects.get(id=11).opening_balance, 0)
