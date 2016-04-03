import random

from django.test import TestCase
from model_mommy import mommy

from dashboard.helpers import *
from dashboard.models import Score, Consumption, AdultPatientsRecord, PAEDPatientsRecord
from dashboard.views.data_sources import NegativesCheckDataSource, ConsumptionAndPatientsDataSource


def generate_values():
    fields = [
        PACKS_ORDERED,
        ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN,
        ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS,
        QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS,
        MONTHS_OF_STOCK_OF_HAND,
        CLOSING_BALANCE,
        LOSES_ADJUSTMENTS,
        ART_CONSUMPTION,
        PMTCT_CONSUMPTION,
        QUANTITY_RECEIVED,
        OPENING_BALANCE
    ]
    data = {}
    for field in fields:
        data[field] = random.randrange(0, 600)
    return data


class NegativesCheckDataSourceTestCase(TestCase):
    def setUp(self):
        name = "F1"
        warehouse = "W1"
        ip = "I1"
        district = "D1"
        cycle = "Jan - Feb 2015"
        self.score = Score.objects.create(name=name, warehouse=warehouse, ip=ip, district=district, REPORTING={DEFAULT: YES},
                                          WEB_BASED={DEFAULT: YES}, cycle=cycle, orderFormFreeOfNegativeNumbers={F1: YES})

    def test_should_show_check_name(self):
        data_source = NegativesCheckDataSource()
        generated_data = data_source.as_array(self.score, ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, F1)
        self.assertEquals(generated_data[1][1], TEST_NAMES.get(ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS))
        self.assertEquals(generated_data[2][0], "")
        self.assertEquals(generated_data[3], ["", "Facility", "District", "Warehouse", "IP", "Cycle", "Result"])
        self.assertEquals(generated_data[4], ["", self.score.name, self.score.district, self.score.warehouse, self.score.ip, self.score.cycle, YES])
        self.assertEquals(generated_data[5][0], "")
        self.assertEquals(generated_data[6][0], "")
        self.assertEquals(generated_data[7][1], "RAW ORDER DATA")


class ConsumptionAndPatientsDataSourceExportTestCase(TestCase):
    formulations = [F1, F2, F3]

    def setUp(self):
        name = "F1"
        warehouse = "W1"
        ip = "I1"
        district = "D1"
        cycle = "Jan - Feb 2015"
        self.score = Score.objects.create(name=name, warehouse=warehouse, ip=ip, district=district, REPORTING={DEFAULT: YES},
                                          WEB_BASED={DEFAULT: YES}, cycle=cycle, consumptionAndPatients={F1: YES})
        for q in F1_PATIENT_QUERY:
            mommy.make(AdultPatientsRecord, name=name, warehouse=warehouse, ip=ip, district=district, cycle=cycle, formulation=q, new=random.randrange(0, 600), existing=random.randrange(0, 600))
            mommy.make(PAEDPatientsRecord, name=name, warehouse=warehouse, ip=ip, district=district, cycle=cycle, formulation=q, new=random.randrange(0, 600), existing=random.randrange(0, 600))
        for formulation in self.formulations:
            values = generate_values()
            mommy.make(Consumption, name=name, warehouse=warehouse, ip=ip, district=district, cycle=cycle, formulation=formulation, **values)

    def test_should_show_check_name(self):
        data_source = ConsumptionAndPatientsDataSource()
        generated_data = data_source.as_array(self.score, CONSUMPTION_AND_PATIENTS, F1)
        self.assertEquals(generated_data[1][1], TEST_NAMES.get(CONSUMPTION_AND_PATIENTS))
        self.assertEquals(generated_data[2][0], "")
        self.assertEquals(generated_data[3], ["","Facility", "District", "Warehouse", "IP", "Cycle", "Result"])
        self.assertEquals(generated_data[4], ["",self.score.name, self.score.district, self.score.warehouse, self.score.ip, self.score.cycle, YES])
        self.assertEquals(generated_data[5][0], "")
        self.assertEquals(generated_data[6][0], "")
        self.assertEquals(generated_data[7][1], "RAW ORDER DATA")

    def test_should_show_consumption_data(self):
        data_source = ConsumptionAndPatientsDataSource()
        generated_data = data_source.as_array(self.score, CONSUMPTION_AND_PATIENTS, F1)
        self.assertEquals(generated_data[7][1], "RAW ORDER DATA")
        self.assertEquals(generated_data[8][1], "CONSUMPTION")
        self.assertEquals(generated_data[8][4], "PATIENTS")
