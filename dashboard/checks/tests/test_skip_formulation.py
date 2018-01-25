from django.test import TestCase

from dashboard.checks.check_preview import skip_formulation


class TestSkip_formulation(TestCase):
    def test_skip_formulation(self):
        self.assertEqual(skip_formulation([['A', 1, 3], ['B', 3, 4]]), [1, 3, 3, 4])
        self.assertEqual(skip_formulation(['A', 1, 3]), [1, 3])
