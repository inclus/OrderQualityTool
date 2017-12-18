from json import loads

from django_webtest import WebTest

from dashboard.models import AdultPatientsRecord


class PreviewLocationsViewTestCase(WebTest):
    def test_that_only_locations_with_data_show_up(self):
        url = "/api/tests/preview/locations"
        AdultPatientsRecord.objects.create(
            name="loc1",
            district="dis1",
            formulation="form_a",
            existing=12,
            new=1,
            cycle="cycle1")
        AdultPatientsRecord.objects.create(
            name="loc1",
            district="dis1",
            formulation="form_a",
            existing=12,
            new=1,
            cycle="cycle2")
        AdultPatientsRecord.objects.create(
            name="loc2",
            district="dis1",
            formulation="form_a",
            existing=12,
            new=1,
            cycle="cycle2")
        AdultPatientsRecord.objects.create(
            name="loc3",
            district="dis1",
            formulation="form_a",
            cycle="cycle3"
        )
        response = self.app.post_json(url, user="testuser", params={
            "type": {"id": "FacilityTwoGroups"},
            "groups": [
                {
                    "name": "G1",
                    "aggregation": {"id": "SUM", "name": "sum"},
                    "cycle": {"id": "current", "name": "current"},
                    "selected_fields": ["new", "existing"],
                    "model": {"id": "Adult", "name": "Adult Records"},
                    "selected_formulations": ["form_a", "form_b"]
                }
            ]
        })
        json_response = response.content.decode('utf8')
        self.assertEqual(200, response.status_code)
        locations = loads(json_response).get('locations', [])
        self.assertEqual(2, len(locations))
        self.assertEqual(locations[0], {"name": "loc1", "district": "dis1", "cycles": ["cycle1", "cycle2"]})
        self.assertEqual(locations[1], {"name": "loc2", "district": "dis1", "cycles": ["cycle2"]})
