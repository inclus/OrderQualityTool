import random

from django.urls import reverse
from django_webtest import WebTest
from model_mommy import mommy

from dashboard.checks.legacy.nn import NNRTIPAEDCheck, NNRTIADULTSCheck
from dashboard.checks.tracer import Tracer
from dashboard.helpers import (
    DEFAULT,
    YES,
    DF1,
    DF2,
    PACKS_ORDERED,
    ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN,
    ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
    QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS,
    MONTHS_OF_STOCK_ON_HAND,
    CLOSING_BALANCE,
    LOSES_ADJUSTMENTS,
    COMBINED_CONSUMPTION,
    QUANTITY_RECEIVED,
    OPENING_BALANCE,
    F1_QUERY,
)
from dashboard.models import Score, Consumption, AdultPatientsRecord, PAEDPatientsRecord

F1_PATIENT_QUERY = ["TDF/3TC/EFV (PMTCT)", "TDF/3TC/EFV (ADULT)"]


def generate_values():
    fields = [
        PACKS_ORDERED,
        ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN,
        ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
        QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS,
        MONTHS_OF_STOCK_ON_HAND,
        CLOSING_BALANCE,
        LOSES_ADJUSTMENTS,
        COMBINED_CONSUMPTION,
        QUANTITY_RECEIVED,
        OPENING_BALANCE,
    ]
    data = {}
    for field in fields:
        data[field] = random.randrange(0, 600)
    return data


class ScoreDetailTestCase():
    formulations = [F1_QUERY]

    def test_view_loads(self):
        name = "F1"
        warehouse = "W1"
        ip = "I1"
        district = "D1"
        cycle = "Jan - Feb 2015"
        score = Score.objects.create(
            name=name,
            warehouse=warehouse,
            ip=ip,
            district=district,
            data={"REPORTING": {DEFAULT: YES}},
            cycle=cycle,
        )
        for q in F1_PATIENT_QUERY:
            mommy.make(
                AdultPatientsRecord,
                name=name,
                warehouse=warehouse,
                ip=ip,
                district=district,
                cycle=cycle,
                formulation=q,
                new=random.randrange(0, 600),
                existing=random.randrange(0, 600),
            )
            mommy.make(
                PAEDPatientsRecord,
                name=name,
                warehouse=warehouse,
                ip=ip,
                district=district,
                cycle=cycle,
                formulation=q,
                new=random.randrange(0, 600),
                existing=random.randrange(0, 600),
            )
        for formulation in self.get_formulations():
            values = generate_values()
            mommy.make(
                Consumption,
                name=name,
                warehouse=warehouse,
                ip=ip,
                district=district,
                cycle=cycle,
                formulation=formulation,
                **values
            )
        url = reverse(
            "scores-detail", kwargs={"id": score.id, "column": self.column}
        ) + "?combination=" + Tracer.F1().key
        response = self.app.get(url)
        self.assertEqual(response.status_code, 200)

    def get_formulations(self):
        return self.formulations


class NNRTICheckTestMixin(ScoreDetailTestCase):
    check = NNRTIPAEDCheck

    def get_formulations(self):
        check = NNRTIPAEDCheck()
        formulations = check.combinations[0].extras[DF1] + check.combinations[0].extras[
            DF2
        ]
        return formulations


class ReportingCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 4


class MultipleOrdersCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 10


class GapsCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 9


class GuideLineAdherenceAdult1LCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 5


class GuideLineAdherenceAdult2LCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 6


class GuideLineAdherencePaed1LCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 7


class NNRTIPaedCheckDetailView(WebTest, NNRTICheckTestMixin):
    check = NNRTIPAEDCheck
    column = 17


class NNRTICurrentAdultCheckDetailView(WebTest, NNRTICheckTestMixin):
    check = NNRTIADULTSCheck
    column = 16


class ConsumptionAndPatientsCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 11


class WarehouseCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 15


class DiffOrdersCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 12


class ClosingBalanceCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 13


class NegativesCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 10


class StableConsumptionCheckDetailView(WebTest, ScoreDetailTestCase):
    column = 14
