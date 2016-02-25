from django.test import TestCase
from dashboard.views.data_sources import NNRTIDataSource

class NNRTIDataSourceTestCase(TestCase):
    def test_correct_template_is_selected(self):
        data_source = NNRTIDataSource()
        self.assertEqual(data_source.get_template(""), "check/nnrti.html")
