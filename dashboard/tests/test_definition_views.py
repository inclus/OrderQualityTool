from json import loads

from django_webtest import WebTest

from dashboard.tests.fake_definition import FakeDefinition, gen_adult_record


class PreviewLocationsViewTestCase(WebTest):
    def test_that_only_locations_with_data_show_up(self):
        url = "/api/tests/preview/locations"
        gen_adult_record()
        gen_adult_record(cycle="cycle2")
        gen_adult_record(name="loc2", cycle="cycle2")
        gen_adult_record(name="loc3", cycle="cycle3", existing=None, new=None)
        response = self.app.post_json(url, user="testuser", params=FakeDefinition().single().get())
        json_response = response.content.decode('utf8')
        self.assertEqual(200, response.status_code)
        locations = loads(json_response).get('locations', [])
        self.assertEqual(2, len(locations))
        self.assertEqual(locations[0], {"name": "loc1", "district": "dis1", "cycles": ["cycle1", "cycle2"]})
        self.assertEqual(locations[1], {"name": "loc2", "district": "dis1", "cycles": ["cycle2"]})
