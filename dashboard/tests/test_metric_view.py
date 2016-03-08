import json
from django_webtest import WebTest
from dashboard.models import CycleFormulationScore
from dashboard.helpers import REPORTING, DEFAULT, WEB_BASED, GUIDELINE_ADHERENCE_PAED_1L, GUIDELINE_ADHERENCE_ADULT_2L, GUIDELINE_ADHERENCE_ADULT_1L
from django.core.urlresolvers import reverse


class ReportMetricTestCase(WebTest):
    def test_that_the_latest_cycle_is_considered(self):
        for test in [REPORTING, WEB_BASED, GUIDELINE_ADHERENCE_ADULT_1L, GUIDELINE_ADHERENCE_ADULT_2L, GUIDELINE_ADHERENCE_PAED_1L]:
            CycleFormulationScore.objects.create(cycle="Jan-Feb 2015", yes=12, test=test, combination=DEFAULT)
            CycleFormulationScore.objects.create(cycle="Jun-Jul 2015", yes=34, test=test, combination=DEFAULT)
        url = reverse("metrics")
        response = self.app.get(url)
        data = json.loads(response.content.decode('utf8'))
        self.assertEquals(data['reporting'], '34.0')
        self.assertEquals(data['webBased'], '34.0')
        self.assertEquals(data['adherence'], '34.0')

    def test_that_the_adherence_type_is_considered_when_avaialble(self):
        for test in [REPORTING, WEB_BASED, GUIDELINE_ADHERENCE_ADULT_1L, GUIDELINE_ADHERENCE_ADULT_2L, GUIDELINE_ADHERENCE_PAED_1L]:
            other = 34
            if test == GUIDELINE_ADHERENCE_PAED_1L:
                other = 56
            CycleFormulationScore.objects.create(cycle="Jan-Feb 2015", yes=12, test=test, combination=DEFAULT)
            CycleFormulationScore.objects.create(cycle="Jun-Jul 2015", yes=other, test=test, combination=DEFAULT)
        url = reverse("metrics") + "?adh=Paed 1L"
        response = self.app.get(url)
        data = json.loads(response.content.decode('utf8'))
        self.assertEquals(data['adherence'], '56.0')
