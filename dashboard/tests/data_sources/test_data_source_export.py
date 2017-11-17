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
        MONTHS_OF_STOCK_ON_HAND,
        CLOSING_BALANCE,
        LOSES_ADJUSTMENTS,
        COMBINED_CONSUMPTION,
        QUANTITY_RECEIVED,
        OPENING_BALANCE
    ]
    data = {}
    for field in fields:
        data[field] = 50
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
        self.assertEquals(generated_data[1][1], get_test_name(ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS))
        self.assertEquals(generated_data[2][0], "")
        self.assertEquals(generated_data[3], ["", "Facility", "District", "Warehouse", "IP", "Cycle", "Formulation", "Result"])
        self.assertEquals(generated_data[4], ["", self.score.name, self.score.district, self.score.warehouse, self.score.ip, self.score.cycle, F1, YES])
        self.assertEquals(generated_data[5][0], "")
        self.assertEquals(generated_data[6][0], "")
        self.assertEquals(generated_data[7][1], "RAW ORDER DATA")


class ConsumptionAndPatientsDataSourceExportTestCase(TestCase):
    def setUp(self):
        name = "F1"
        warehouse = "W1"
        ip = "I1"
        district = "D1"
        cycle = "Jan - Feb 2015"
        self.score = Score.objects.create(name=name, warehouse=warehouse, ip=ip, district=district, REPORTING={DEFAULT: YES},
                                          WEB_BASED={DEFAULT: YES}, cycle=cycle, consumptionAndPatients={F1: YES})
        for q in F1_PATIENT_QUERY:
            mommy.make(AdultPatientsRecord, name=name, warehouse=warehouse, ip=ip, district=district, cycle=cycle, formulation=q, new=50, existing=50)
            mommy.make(PAEDPatientsRecord, name=name, warehouse=warehouse, ip=ip, district=district, cycle=cycle, formulation=q, new=100, existing=100)
        for formulation in [F1_QUERY]:
            values = generate_values()
            mommy.make(Consumption, name=name, warehouse=warehouse, ip=ip, district=district, cycle=cycle, formulation=formulation, **values)

    def test_should_show_check_name(self):
        data_source = ConsumptionAndPatientsDataSource()
        generated_data = data_source.as_array(self.score, CONSUMPTION_AND_PATIENTS, F1)
        self.assertEquals(generated_data[1][1], get_test_name(CONSUMPTION_AND_PATIENTS))
        self.assertEquals(generated_data[2][0], "")
        self.assertEquals(generated_data[3], ["", "Facility", "District", "Warehouse", "IP", "Cycle", "Formulation", "Result"])
        self.assertEquals(generated_data[4], ["", self.score.name, self.score.district, self.score.warehouse, self.score.ip, self.score.cycle, F1, YES])
        self.assertEquals(generated_data[5][0], "")
        self.assertEquals(generated_data[6][0], "")
        self.assertEquals(generated_data[7][1], "RAW ORDER DATA")

    def test_should_show_consumption_data(self):
        data_source = ConsumptionAndPatientsDataSource()
        generated_data = data_source.as_array(self.score, CONSUMPTION_AND_PATIENTS, F1)
        self.assertEquals(generated_data[7][1], "RAW ORDER DATA")
        self.assertEquals(generated_data[8][1], "CONSUMPTION")
        self.assertEquals(generated_data[8][4], "PATIENTS")
        self.assertEquals(generated_data[9], [])
        self.assertEquals(generated_data[10], ["", F1_QUERY, "", "", F1_PATIENT_QUERY[0], ""])
        self.assertEquals(generated_data[11], ["", FIELD_NAMES.get(COMBINED_CONSUMPTION), 50, "", FIELD_NAMES.get(NEW), 50])
        self.assertEquals(generated_data[12], ["", TOTAL, 50, "", FIELD_NAMES.get(EXISTING), 50])
        self.assertEquals(generated_data[13], ["", "", "", "", TOTAL, 100])
        self.assertEquals(generated_data[14], [])
        self.assertEquals(generated_data[15], ["", "", "", "", F1_PATIENT_QUERY[1], ""])
        self.assertEquals(generated_data[16], ["", "", "", "", FIELD_NAMES.get(NEW), 50])
        self.assertEquals(generated_data[17], ["", "", "", "", FIELD_NAMES.get(EXISTING), 50])
        self.assertEquals(generated_data[18], ["", "", "", "", TOTAL, 100])
        self.assertEquals(generated_data[19], [])
        self.assertEquals(generated_data[20], [])
        self.assertEquals(generated_data[21], ["", "Conversion Ratio (packs per patient, bimonthly)"])
        self.assertEquals(generated_data[22], ["", F1_QUERY, 2.0])
        self.assertEquals(generated_data[23], [])
        self.assertEquals(generated_data[24], [])
        self.assertEquals(generated_data[25], ["", "ESTIMATED CURRENT PATIENTS"])
        self.assertEquals(generated_data[26], ["", "From Consumption Data", "", "", "From Patient Data"])
        self.assertEquals(generated_data[27], ["", F1_QUERY, 25.0, "", F1_PATIENT_QUERY[0], 100.0])
        self.assertEquals(generated_data[28], ["", "TOTAL", 25.0, "", "TDF/3TC/EFV (ADULT)", 100.0])
        self.assertEquals(generated_data[29], ["", "", "", "", "TOTAL", 200])
