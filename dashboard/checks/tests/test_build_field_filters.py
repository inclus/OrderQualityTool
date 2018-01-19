from django.test import TestCase

from dashboard.checks.check_preview import build_field_filters


class TestFieldFilters(TestCase):
    def test_each_field_gets_is_null_filter(self):
        filters_kwargs = build_field_filters(['new', 'existing'])
        self.assertEqual({"new__isnull": False, "existing__isnull": False}, filters_kwargs)
