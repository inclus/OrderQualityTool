from unittest import TestCase

from dashboard.data.entities import Location


class TestLocation(TestCase):

    def test_location_works_as_key(self):
        facility = "Home"
        district = "dis"
        partner = "p"
        warehouse = "JMS"

        location = Location(
            facility=facility, district=district, partner=partner, warehouse=warehouse
        )

        data = {location: 1}
        other_location = Location(
            district=district, facility=facility, partner=partner, warehouse="JMS"
        )
        self.assertEqual(data.get(other_location), 1)
