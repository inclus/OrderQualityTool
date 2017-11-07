import os

from django.test import TestCase

from dashboard.data.entities import ReportOutput, Location
from dashboard.data.html_data_import import extract_locations_and_import_records, HtmlDataImport
from dashboard.helpers import PAED_PATIENT_REPORT, ADULT_PATIENT_REPORT, CONSUMPTION_REPORT
from dashboard.models import Dhis2StandardReport, LocationToPartnerMapping, MAUL, JMS


def get_fixture_path(name):
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
    return file_path


def get_test_output_from_fixture(name, report_type=PAED_PATIENT_REPORT, warehouse=MAUL):
    path = get_fixture_path(name)
    fixture = open(path, "r").read()
    report = Dhis2StandardReport.objects.filter(report_type=report_type, warehouse=warehouse).first()
    return [ReportOutput(output=fixture, report=report)]


class LocationImportTestCase(TestCase):
    def test_that_correct_number_of_locations_are_extracted(self):
        locations, records = extract_locations_and_import_records(
            get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
            LocationToPartnerMapping.get_mapping())
        self.assertEqual(len(locations), 5)

    def test_that_location_has_implementing_partner(self):
        locations, records = extract_locations_and_import_records(
            get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
            LocationToPartnerMapping.get_mapping())
        first_location = locations[0]
        self.assertEqual(first_location.facility, "Ococia (Orungo) St. Clare HC III")
        self.assertEqual(first_location.partner, "Unknown")
        third_location = locations[2]
        self.assertEqual(third_location.facility, "St. Francis Acumet HC III")
        self.assertEqual(third_location.partner, "TASO")

    def test_that_location_has_warehouse(self):
        locations, records = extract_locations_and_import_records(
            get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
            LocationToPartnerMapping.get_mapping())
        first_location = locations[0]
        self.assertEqual(first_location.facility, "Ococia (Orungo) St. Clare HC III")
        self.assertEqual(first_location.warehouse, "MAUL")


class AdultImportTestCase(TestCase):
    def setUp(self):
        self.test_location = Location(facility="AAR Acacia Clinic HC II", subcounty="Kampala Central Division",
                                      district="Kampala District",
                                      region="Central Region", partner="UHMG", warehouse=JMS)

        fixture = get_test_output_from_fixture("arv-2-adult-pmtct-art-patient-report-all-regimen-jms.html",
                                               report_type=ADULT_PATIENT_REPORT, warehouse=JMS)
        self.data_import = HtmlDataImport(fixture,
                                          None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.ads[self.test_location]
        self.assertEqual(len(records_for_first_location), 12)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.ads[self.test_location]
        first_record = records_for_first_location[0]
        self.assertEqual(first_record.location, self.test_location)
        self.assertEqual(first_record.regimen, "TDF/3TC/ATV/r (ADULT)")
        self.assertEqual(first_record.existing, 2)
        self.assertEqual(first_record.new, 1)

        seventh_record = records_for_first_location[11]
        self.assertEqual(seventh_record.location, self.test_location)
        self.assertEqual(seventh_record.regimen, "TDF/3TC/NVP (PMTCT)")
        self.assertEqual(seventh_record.existing, 1)
        self.assertEqual(seventh_record.new, 0)

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.ads), 110)


class PaedImportTestCase(TestCase):
    def setUp(self):
        self.test_location = Location(facility="Ongutoi HC III", subcounty="Abarilela Subcounty",
                                      district="Amuria District",
                                      region="Eastern Region", partner="TASO", warehouse=MAUL)

        self.data_import = HtmlDataImport(get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
                                          None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.pds[self.test_location]
        self.assertEqual(len(records_for_first_location), 7)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.pds[self.test_location]
        first_record = records_for_first_location[0]
        self.assertEqual(first_record.location, self.test_location)
        self.assertEqual(first_record.regimen, "ABC/3TC/EFV")
        self.assertEqual(first_record.existing, 1)
        self.assertEqual(first_record.new, 0)

        seventh_record = records_for_first_location[6]
        self.assertEqual(seventh_record.location, self.test_location)
        self.assertEqual(seventh_record.regimen, "AZT/3TC/NVP")
        self.assertEqual(seventh_record.existing, 2)
        self.assertEqual(seventh_record.new, 0)

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.pds), 5)


class ConsumptionImportTestCase(TestCase):
    def setUp(self):
        self.test_location = Location(facility="Health Initiative Association Uganda",
                                      subcounty="Buikwe Town Council",
                                      district="Buikwe District",
                                      region="Central Region", partner="PHS", warehouse=MAUL)

        self.data_import = HtmlDataImport(
            get_test_output_from_fixture("arv-0-consumption-data-report-maul.html", report_type=CONSUMPTION_REPORT),
            None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.cs[self.test_location]
        self.assertEqual(len(records_for_first_location), 1)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.cs[self.test_location]
        first_record = records_for_first_location[0]
        self.assertEqual(first_record.location, self.test_location)
        self.assertEqual(first_record.regimen,
                         "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]")
        self.assertEqual(first_record.opening_balance, 280)
        self.assertEqual(first_record.quantity_received, 204)
        self.assertEqual(first_record.consumption, 169)
        self.assertEqual(first_record.loses_adjustments, 0)
        self.assertEqual(first_record.months_of_stock_on_hand, 3)
        self.assertEqual(first_record.quantity_required_for_current_patients, 98)
        self.assertEqual(first_record.number_of_new_art_patients, 10)
        self.assertEqual(first_record.number_of_new_pregnant_women, 10)
        self.assertEqual(first_record.packs_ordered, 178)

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.cs), 7)
