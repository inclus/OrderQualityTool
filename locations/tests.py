from django.test import TestCase

from locations.models import import_locations_from_json, Location


class ImportLocationsTestCase(TestCase):
    def test_should_import_locations_into_tree(self):
        self.assertEqual(Location.objects.count(), 0)
        json_text = """{"organisationUnits":[{"id":"Ugl9pT2K5B0","level":5,"name":"01 Commando HC II","parent":{"id":"PrIDcobIQsW","level":4,"name":"Okwang Subcounty"}}]}"""
        import_locations_from_json(json_text)
        self.assertEqual(Location.objects.count(), 2)
        level_5_location = Location.objects.get(uid="Ugl9pT2K5B0")
        self.assertEqual(level_5_location.org_level, "5")
        self.assertEqual(level_5_location.name, "01 Commando HC II")
        self.assertEqual(level_5_location.parent.org_level, "4")
        self.assertEqual(level_5_location.parent.name, "Okwang Subcounty")
