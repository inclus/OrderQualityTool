import os

import responses
from django.test import TestCase
from hamcrest import *

from dashboard.data.entities import ReportOutput, Location
from dashboard.data.html_data_import import extract_locations_and_import_records, HtmlDataImport
from dashboard.helpers import PAED_PATIENT_REPORT, ADULT_PATIENT_REPORT, CONSUMPTION_REPORT
from dashboard.medist.tests.test_helpers import fake_orgunit_response
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
    @responses.activate
    @fake_orgunit_response()
    def test_that_correct_number_of_locations_are_extracted(self):
        locations, records = extract_locations_and_import_records(
            get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
            LocationToPartnerMapping.get_mapping())
        self.assertEqual(len(locations), 2115)

    # @responses.activate
    # @fake_orgunit_response()
    # def test_that_locations_are_unique_by_name_and_district_only(self):
    #     outputs = get_test_output_from_fixture("uniq.html", report_type=CONSUMPTION_REPORT, warehouse=MAUL)
    #     outputs.extend(get_test_output_from_fixture("uniq.html", report_type=CONSUMPTION_REPORT, warehouse=JMS))
    #     locations, records = extract_locations_and_import_records(
    #         outputs,
    #         LocationToPartnerMapping.get_mapping())
    #     self.assertEqual(len(locations), 1)

    @responses.activate
    @fake_orgunit_response()
    def test_that_location_has_implementing_partner(self):
        locations, records = extract_locations_and_import_records(
            get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
            LocationToPartnerMapping.get_mapping())

        assert_that(locations, has_item(
            all_of(
                has_property("facility", "St. Michael Kanyike HC III"),
                has_property("partner", "Unknown"),
            )
        ))

        assert_that(locations, has_item(
            all_of(
                has_property("facility", "St. Monica Katende HC III"),
                has_property("partner", "RHSP"),
            )
        ))

    @responses.activate
    @fake_orgunit_response()
    def test_that_location_has_warehouse(self):
        locations, records = extract_locations_and_import_records(
            get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
            LocationToPartnerMapping.get_mapping())
        assert_that(locations, has_item(
            all_of(
                has_property("facility", "Medical Research Center Clinic"),
                has_property("warehouse", "MAUL"),
            )
        ))


class AdultImportTestCase(TestCase):
    @responses.activate
    @fake_orgunit_response()
    def setUp(self):
        self.test_location = Location(facility="AAR Acacia Clinic HC II",
                                      district="Kampala District",
                                      partner="UHMG",
                                      status="reporting",
                                      warehouse=JMS)

        fixture = get_test_output_from_fixture("arv-2-adult-pmtct-art-patient-report-all-regimen-jms.html",
                                               report_type=ADULT_PATIENT_REPORT, warehouse=JMS)
        self.data_import = HtmlDataImport(fixture,
                                          None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.ads[self.test_location]
        self.assertEqual(len(records_for_first_location), 12)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.ads[self.test_location]
        assert_that(records_for_first_location, has_item(all_of(
            has_property("formulation", "TDF/3TC/EFV (PMTCT)"),
            has_property("existing", 7),
            has_property("new", 0),
            has_property("location", self.test_location)
        )))

        assert_that(records_for_first_location, has_item(all_of(
            has_property("formulation", "TDF/3TC/ATV/r (ADULT)"),
            has_property("existing", 2),
            has_property("new", 1),
            has_property("location", self.test_location)
        )))

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.ads), 110)


class PaedImportTestCase(TestCase):
    @responses.activate
    @fake_orgunit_response()
    def setUp(self):
        self.test_location = Location(facility="AAR Acacia Clinic HC II",
                                      district="Kampala District",
                                      partner="TASO",
                                      status="reporting",
                                      warehouse=MAUL)

        self.data_import = HtmlDataImport(get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"),
                                          None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.pds[self.test_location]
        self.assertEqual(len(records_for_first_location), 12)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.pds[self.test_location]

        assert_that(records_for_first_location, has_item(all_of(
            has_property("formulation", "TDF/3TC/ATV/r (ADULT)"),
            has_property("existing", 2),
            has_property("new", 1),
            has_property("location", self.test_location)
        )))

        assert_that(records_for_first_location, has_item(all_of(
            has_property("formulation", "TDF/3TC/EFV (PMTCT)"),
            has_property("existing", 0),
            has_property("new", 0),
            has_property("location", self.test_location)
        )))

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.pds), 1)


class PaedImportCombinedTestCase(TestCase):
    @responses.activate
    @fake_orgunit_response()
    def setUp(self):
        self.test_location = Location(facility="AAR Acacia Clinic HC II",
                                      status="reporting",
                                      district="Kampala District", partner="TASO", warehouse=MAUL)

        results = get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html")
        results.extend(get_test_output_from_fixture("arv-2-paediatric-art-patient-report-maul.html"))
        self.data_import = HtmlDataImport(results,
                                          None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.pds[self.test_location]
        self.assertEqual(len(records_for_first_location), 12)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.pds[self.test_location]
        assert_that(records_for_first_location, has_item(all_of(
            has_property("formulation", "TDF/3TC/ATV/r (ADULT)"),
            has_property("existing", 4),
            has_property("new", 2),
            has_property("location", self.test_location)
        )))

        assert_that(records_for_first_location, has_item(all_of(
            has_property("formulation", "TDF/3TC/EFV (ADULT)"),
            has_property("existing", 136),
            has_property("new", 4),
            has_property("location", self.test_location)
        )))

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.pds), 1)


class ConsumptionImportTestCase(TestCase):
    @responses.activate
    @fake_orgunit_response()
    def setUp(self):
        self.test_location = Location(facility="Health Initiative Association Uganda",
                                      district="Buikwe District",
                                      status="reporting",
                                      partner="PHS", warehouse=MAUL)

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
        self.assertEqual(first_record.formulation,
                         "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]")
        self.assertEqual(first_record.opening_balance, 280)
        self.assertEqual(first_record.quantity_received, 204)
        self.assertEqual(first_record.consumption, 169)
        self.assertEqual(first_record.loses_adjustments, 0)
        self.assertEqual(first_record.months_of_stock_on_hand, 3)
        self.assertEqual(first_record.quantity_required_for_current_patients, 98)
        self.assertEqual(first_record.estimated_number_of_new_patients, 10)
        self.assertEqual(first_record.estimated_number_of_new_pregnant_women, 10)
        self.assertEqual(first_record.packs_ordered, 178)

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.cs), 6)


class ConsumptionCombinedImportTestCase(TestCase):
    @responses.activate
    @fake_orgunit_response()
    def setUp(self):
        self.test_location = Location(facility="Health Initiative Association Uganda",
                                      district="Buikwe District",
                                      status="reporting",
                                      partner="PHS", warehouse=MAUL)

        fixture = get_test_output_from_fixture("arv-0-consumption-data-report-maul.html",
                                               report_type=CONSUMPTION_REPORT)
        fixture.extend(get_test_output_from_fixture("arv-0-consumption-data-report-maul.html",
                                                    report_type=CONSUMPTION_REPORT))
        self.data_import = HtmlDataImport(
            fixture,
            None).load(LocationToPartnerMapping.get_mapping())

    def test_that_test_location_has_records(self):
        records_for_first_location = self.data_import.cs[self.test_location]
        self.assertEqual(len(records_for_first_location), 1)

    def test_that_test_location_records_have_correct_values(self):
        records_for_first_location = self.data_import.cs[self.test_location]
        first_record = records_for_first_location[0]
        self.assertEqual(first_record.location, self.test_location)
        self.assertEqual(first_record.formulation,
                         "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]")
        self.assertEqual(first_record.opening_balance, 560)
        self.assertEqual(first_record.quantity_received, 408)
        self.assertEqual(first_record.consumption, 338)
        self.assertEqual(first_record.loses_adjustments, 0)
        self.assertEqual(first_record.months_of_stock_on_hand, 6)
        self.assertEqual(first_record.quantity_required_for_current_patients, 196)
        self.assertEqual(first_record.estimated_number_of_new_patients, 20)
        self.assertEqual(first_record.estimated_number_of_new_pregnant_women, 20)
        self.assertEqual(first_record.packs_ordered, 356)

    def test_that_correct_number_of_records_are_extracted(self):
        self.assertEqual(len(self.data_import.cs), 6)
