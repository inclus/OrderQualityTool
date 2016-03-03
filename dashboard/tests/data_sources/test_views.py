from django.core.urlresolvers import reverse
from django_webtest import WebTest

from dashboard.helpers import DEFAULT, YES, F1
from dashboard.models import Score


class ScoreDetailTestCase():
    def test_view_loads(self):
        score = Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={DEFAULT: YES},
                                     WEB_BASED={DEFAULT: YES}, pass_count=2, fail_count=0, cycle="Jan - Feb 2015")
        url = reverse("scores-detail", kwargs={"id": score.id, "column": self.column}) + "?combination=" + F1
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_rendered(self):
        score = Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={DEFAULT: YES},
                                     WEB_BASED={DEFAULT: YES}, pass_count=2, fail_count=0, cycle="Jan - Feb 2015")
        url = reverse("scores-detail", kwargs={"id": score.id, "column": self.column}) + "?combination=" + F1
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template_name)


class ReportingCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 4
    template_name = "check/base.html"


class OrderTypeCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 5
    template_name = "check/base.html"


class MultipleOrdersCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 6
    template_name = "check/base.html"


class GapsCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 7
    template_name = "check/base.html"


class GuideLineAdherenceAdult1LCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 8
    template_name = "check/adherence.html"


class GuideLineAdherenceAdult2LCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 9
    template_name = "check/adherence.html"


class GuideLineAdherencePaed1LCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 10
    template_name = "check/adherence.html"


class NNRTINewPaedCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 11
    template_name = "check/nnrti.html"


class NNRTICurrentPaedCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 12
    template_name = "check/nnrti.html"


class NNRTINewAdultCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 13
    template_name = "check/nnrti.html"


class NNRTICurrentAdultCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 14
    template_name = "check/nnrti.html"


class StablePatientsCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 15
    template_name = "check/differentOrdersOverTime.html"


class ConsumptionAndPatientsCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 16
    template_name = "check/consumptionAndPatients.html"


class WarehouseCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 17
    template_name = "check/differentOrdersOverTime.html"


class DiffOrdersCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 18
    template_name = "check/differentOrdersOverTime.html"


class ClosingBalanceCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 19
    template_name = "check/differentOrdersOverTime.html"


class NegativesCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 20
    template_name = "check/orderFormFreeOfNegativeNumbers.html"


class StableConsumptionCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 21
    template_name = "check/differentOrdersOverTime.html"
