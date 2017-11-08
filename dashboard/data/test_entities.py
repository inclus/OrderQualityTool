from unittest import TestCase

from dashboard.data.entities import Location


class TestLocation(TestCase):
    def test_location_works_as_key(self):
        facility = "Home"
        subcounty = "subcounty"
        district = "dis"
        region = "region"
        partner = "p"
        warehouse = "JMS"

        location = Location(
            facility=facility,
            subcounty=subcounty,
            district=district,
            region=region,
            partner=partner,
            warehouse=warehouse
        )

        data = {location: 1}
        other_location = Location(
            subcounty=subcounty,
            district=district,
            region=region,
            facility=facility,
            partner=partner,
            warehouse="JMS"
        )
        self.assertEqual(data.get(other_location), 1)
