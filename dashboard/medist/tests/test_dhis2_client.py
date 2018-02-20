import responses
from django.test import TestCase

from dashboard.data.entities import Location
from dashboard.medist.client import dhis2_facility_as_location, get_all_locations
from dashboard.medist.tests.test_helpers import fake_orgunit_response


class TestDHIS2FacilityAsLocation(TestCase):
    def test_dhis2_facility_as_location(self):
        data = {
            "level": 5,
            "name": "01 Commando HC II",
            "id": "Ugl9pT2K5B0",
            "ancestors": [
                {
                    "name": "MOH - Uganda",
                    "level": 1
                },
                {
                    "name": "Northern Region",
                    "level": 2
                },
                {
                    "name": "Otuke District",
                    "level": 3
                },
                {
                    "name": "Okwang Subcounty",
                    "level": 4
                }
            ]
        }
        loc = Location.migrate_from_dict({"name": "01 Commando HC II", "District": "Otuke District"})
        location = dhis2_facility_as_location({"01 Commando HC II": "PT"}, {
            loc: loc})(data)
        self.assertEqual(location.facility, "01 Commando HC II")
        self.assertEqual(location.district, "Otuke District")
        self.assertEqual(location.warehouse, "")
        self.assertEqual(location.status, "Reporting")
        self.assertEqual(location.partner, "PT")


class TestGetAllLocations(TestCase):
    @responses.activate
    @fake_orgunit_response()
    def test_should_parse_json_response(self):
        locations = get_all_locations({}, {})
        self.assertEqual(len(locations), 50)
