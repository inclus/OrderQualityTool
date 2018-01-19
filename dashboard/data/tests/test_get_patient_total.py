from django.test import TestCase
from hamcrest import *

from dashboard.data.entities import PatientRecord, Location, RegimenLocationCombination
from dashboard.checks.legacy.check import get_patient_total


class TestGet_patient_total(TestCase):
    def test_get_patient_total_should_handle_strings(self):
        records = [
            PatientRecord(formulation=u'TDF/3TC/EFV (PMTCT)',
                          location=Location(facility=u'Bugongi HC III', district=u'Sheema District',
                                            partner=u'RHITES SW', warehouse=u'NMS', multiple='', status=''),
                          regimen_location=RegimenLocationCombination(
                              location=Location(facility=u'Bugongi HC III', district=u'Sheema District',
                                                partner=u'RHITES SW', warehouse=u'NMS', multiple='', status=''),
                              formulation=u'TDF/3TC/EFV (PMTCT)'), existing=u'', new=8),

        ]
        total = get_patient_total(records)
        assert_that(total, equal_to(8))
