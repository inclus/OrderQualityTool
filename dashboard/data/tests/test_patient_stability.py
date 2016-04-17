from django.test import TestCase

from dashboard.data.cycles import StablePatientVolumesCheck
from dashboard.helpers import NOT_REPORTING


class PatientStabilityTestCase(TestCase):
    def xtest_that_check_fails_if_30_in_prev_and_59_in_next(self):
        check = StablePatientVolumesCheck({}, {})
        current_population = 30
        prev_population = 59
        result = NOT_REPORTING
        data_is_sufficient = True
        include_record = True
        result = check.run_calculation(current_population, prev_population, result, data_is_sufficient, include_record)
        self.assertEquals(result, "YES")
