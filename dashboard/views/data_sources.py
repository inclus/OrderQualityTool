import pydash

from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.helpers import FIELD_NAMES, CONSUMPTION_QUERY, FIELDS, NEW, EXISTING, F1, F2, F3, F1_QUERY, F2_QUERY, F3_QUERY, NAME, IS_ADULT, PATIENT_QUERY, RATIO
from dashboard.models import Consumption, AdultPatientsRecord, PAEDPatientsRecord

query_map = {F1: F1_QUERY, F2: F2_QUERY, F3: F3_QUERY}


def get_combination(combinations, name):
    return pydash.select(combinations, lambda x: x[NAME] == name)[0]


class CheckDataSource():
    def load(self):
        pass


class NegativesCheckDataSource(CheckDataSource):
    def load(self, score, test, combination):
        return self.get_negatives_data(score, test, combination)

    def get_negatives_data(self, score, test, combination):
        check = NegativeNumbersQualityCheck({})
        formulation_query = query_map.get(combination)
        consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__icontains=formulation_query)
        tables = []
        for consumption in consumption_records:
            formulation_data = {"name": consumption.formulation}
            records = []
            for field in check.fields:
                records.append({"column": FIELD_NAMES.get(field), "value": getattr(consumption, field)})
            formulation_data['records'] = records
            tables.append(formulation_data)
        return {"main_title": "RAW ORDER DATA", "template": "#%s" % test, "formulations": tables}


def values_for_models(fields, models):
    output = []
    for obj in models:
        for field in fields:
            value = getattr(obj, field)
            output.append(value)
    return output


class ConsumptionAndPatientsDataSource(CheckDataSource):
    def load(self, score, test, combination):
        return self.get_consumption_and_patients(score, test, combination)

    def get_consumption_and_patients(self, score, test, combination_name):
        check = ConsumptionAndPatientsQualityCheck({})
        check_combination = get_combination(check.combinations, combination_name)
        formulation_query = check_combination.get(CONSUMPTION_QUERY)
        consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__icontains=formulation_query)
        model = AdultPatientsRecord if check_combination.get(IS_ADULT, False) else PAEDPatientsRecord
        patient_records = model.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__in=check_combination.get(PATIENT_QUERY))

        return {
            "main_title": "RAW ORDER DATA",
            "template": "#%s" % test,
            "consumption": (self.calculate_consumption_tables(check_combination, consumption_records)),
            "patients": (self.calculate_patient_tables(patient_records)),
            "packs": (self.calculate_packs(check_combination)),
            "patient_totals": (self.calculate_patient_totals(patient_records)),
            "consumption_totals": (self.calculate_consumption_totals(check_combination, consumption_records))
        }

    def calculate_packs(self, check_combination):
        packs = [{"column": check_combination.get(CONSUMPTION_QUERY), "value": check_combination.get(RATIO)}]
        return packs

    def calculate_consumption_totals(self, check_combination, consumption_records):
        totals = []
        total = 0
        for consumption in consumption_records:
            entry = {"column": consumption.formulation}
            values = values_for_models(check_combination.get(FIELDS, []), [consumption])
            sum = pydash.chain(values).reject(lambda x: x is None).sum().value()
            entry["value"] = sum
            total += sum
            totals.append(entry)
        totals.append({"column": "TOTAL", "value": total, "isHeader": True})
        return totals

    def calculate_consumption_tables(self, check_combination, consumption_records):
        tables = []
        for consumption in consumption_records:
            formulation_data = {"name": consumption.formulation}
            records = []
            sum = 0
            for field in check_combination.get(FIELDS, []):
                value = getattr(consumption, field)
                sum += value
                records.append({"column": FIELD_NAMES.get(field), "value": value})
            records.append({"column": "Total", "value": sum})

            formulation_data['records'] = records
            tables.append(formulation_data)
        return tables

    def calculate_patient_tables(self, patient_records):
        patient_tables = []
        for pr in patient_records:
            formulation_data = {"name": pr.formulation}
            records = []
            sum = 0
            for field in [NEW, EXISTING]:
                value = getattr(pr, field)
                sum += value
                records.append({"column": FIELD_NAMES.get(field), "value": value})
            records.append({"column": "Total", "value": sum})
            formulation_data['records'] = records
            patient_tables.append(formulation_data)
        return patient_tables

    def calculate_patient_totals(self, patient_records):
        patient_totals = []
        total = 0
        for pr in patient_records:
            entry = {"column": pr.formulation}
            values = values_for_models([NEW, EXISTING], [pr])
            sum = pydash.chain(values).reject(lambda x: x is None).sum().value()
            entry["value"] = sum
            total += sum
            patient_totals.append(entry)
        patient_totals.append({"column": "TOTAL", "value": total, "isHeader": True})
        return patient_totals
