from collections import defaultdict

import pydash

from dashboard.data.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckAdult2L, GuidelineAdherenceCheckPaed1L
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.cycles import OrdersOverTimeCheck, BalancesMatchCheck, StableConsumptionCheck, StablePatientVolumesCheck
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.helpers import FIELD_NAMES, CONSUMPTION_QUERY, FIELDS, NEW, EXISTING, F1, F2, F3, F1_QUERY, F2_QUERY, F3_QUERY, NAME, IS_ADULT, PATIENT_QUERY, RATIO, get_prev_cycle, CLOSING_BALANCE, OPENING_BALANCE, ADULT, PACKS_ORDERED, QUANTITY_RECEIVED, GUIDELINE_ADHERENCE_ADULT_1L, GUIDELINE_ADHERENCE_ADULT_2L, GUIDELINE_ADHERENCE_PAED_1L, DF1, DF2
from dashboard.models import Consumption, AdultPatientsRecord, PAEDPatientsRecord

COLUMN = "column"

TOTAL = "TOTAL"

query_map = {F1: F1_QUERY, F2: F2_QUERY, F3: F3_QUERY}


def get_combination(combinations, name):
    return pydash.select(combinations, lambda x: x[NAME] == name)[0]


class CheckDataSource():
    def __init__(self):
        pass

    def load(self, score, test, combination):
        data = self.get_context(score, test, combination)
        data["template"] = self.get_template(test)
        return data

    def get_template(self, test):
        return "check/%s.html" % test

    def get_context(self, score, test, combination):
        raise NotImplementedError()


class NegativesCheckDataSource(CheckDataSource):
    def get_context(self, score, test, combination):
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
        return {"main_title": "RAW ORDER DATA", "formulations": tables}


def values_for_models(fields, models):
    output = []
    for obj in models:
        for field in fields:
            value = getattr(obj, field)
            output.append(value)
    return output


class ConsumptionAndPatientsDataSource(CheckDataSource):
    def get_context(self, score, test, combination):
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
            entry = {COLUMN: consumption.formulation}
            values = values_for_models(check_combination.get(FIELDS, []), [consumption])
            sum = pydash.chain(values).reject(lambda x: x is None).sum().value()
            entry["value"] = sum
            total += sum
            totals.append(entry)
        totals.append({COLUMN: TOTAL, "value": total, "isHeader": True})
        return totals

    def calculate_consumption_tables(self, check_combination, consumption_records):
        tables = []
        for consumption in consumption_records:
            formulation_data = {"name": consumption.formulation}
            records = []
            sum = 0
            for field in check_combination.get(FIELDS, []):
                value = getattr(consumption, field)
                sum += int(value)
                records.append({COLUMN: FIELD_NAMES.get(field), "value": value})
            records.append({COLUMN: TOTAL, "value": sum, "isHeader": True})

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
                sum += int(value)
                records.append({COLUMN: FIELD_NAMES.get(field), "value": value})
            records.append({COLUMN: TOTAL, "value": sum, "isHeader": True})
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
            total += int(sum)
            patient_totals.append(entry)
        patient_totals.append({"column": TOTAL, "value": total, "isHeader": True})
        return patient_totals


class TwoCycleDataSource(CheckDataSource):
    check = OrdersOverTimeCheck({}, {})

    def get_context(self, score, test, combination):

        current_cycle = score.cycle
        prev_cycle = get_prev_cycle(current_cycle)

        return {
            "main_title": "RAW ORDER DATA",
            "previous_cycle": self.get_table_for_cycle(prev_cycle, self.check, combination, score),
            "current_cycle": self.get_table_for_cycle(current_cycle, self.check, combination, score),
        }

    def get_table_for_cycle(self, cycle, check, combination, score):
        check_combination = get_combination(check.combinations, combination)
        records = self.get_queryset(check_combination, cycle, score)
        tables = [
            {"cycle": cycle}
        ]
        tables[0]["rows"] = self.build_rows(check, records)
        return tables

    def get_queryset(self, check_combination, cycle, score):
        formulation_query = check_combination.get(CONSUMPTION_QUERY)
        records = Consumption.objects.filter(name=score.name, district=score.district, cycle=cycle, formulation__icontains=formulation_query)
        return records

    def build_rows(self, check, consumption_records):
        rows = []
        for consumption in consumption_records:
            for field in check.fields:
                value = getattr(consumption, field)
                rows.append({"column": FIELD_NAMES.get(field), "value": value})
        return rows


class ClosingBalanceMatchesOpeningBalanceDataSource(CheckDataSource):
    check = BalancesMatchCheck({}, {})

    def get_template(self, test):
        return "check/differentOrdersOverTime.html"

    def get_context(self, score, test, combination):
        current_cycle = score.cycle
        prev_cycle = get_prev_cycle(current_cycle)
        return {
            "main_title": "RAW ORDER DATA",
            "previous_cycle": self.get_table_for_cycle(prev_cycle, self.check, combination, score, [CLOSING_BALANCE]),
            "current_cycle": self.get_table_for_cycle(current_cycle, self.check, combination, score, [OPENING_BALANCE]),
        }

    def get_table_for_cycle(self, cycle, check, combination, score, fields):
        check_combination = get_combination(check.combinations, combination)
        formulation_query = check_combination.get(CONSUMPTION_QUERY)
        consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=cycle, formulation__icontains=formulation_query)
        tables = [
            {"cycle": cycle}
        ]
        rows = []
        for consumption in consumption_records:
            for field in fields:
                value = getattr(consumption, field)
                rows.append({"column": FIELD_NAMES.get(field), "value": value})
        tables[0]["rows"] = rows
        return tables


class StableConsumptionDataSource(TwoCycleDataSource):
    check = StableConsumptionCheck({}, {})

    def get_template(self, test):
        return "check/differentOrdersOverTime.html"

    def build_rows(self, check, consumption_records):
        rows = []

        for consumption in consumption_records:
            tot = 0
            for field in check.fields:
                value = getattr(consumption, field)
                tot += int(value)
                rows.append({"column": FIELD_NAMES.get(field), "value": value})
            rows.append({"column": TOTAL, "value": tot, "isHeader": True})
        return rows


class StablePatientVolumesDataSource(TwoCycleDataSource):
    def get_template(self, test):
        return "check/differentOrdersOverTime.html"

    check = StablePatientVolumesCheck({}, {})

    def build_rows(self, check, records):
        rows = []
        for consumption in records:
            rows.append({"column": consumption.formulation, "isHeader": True})
            tot = 0
            for field in check.fields:
                value = getattr(consumption, field)
                tot = int(value)
                rows.append({"column": FIELD_NAMES.get(field), "value": value})
            rows.append({"column": TOTAL, "value": tot, "isHeader": True})
        return rows

    def get_queryset(self, check_combination, cycle, score):
        query = check_combination.get(PATIENT_QUERY)
        model = AdultPatientsRecord if check_combination.get(ADULT, False) else PAEDPatientsRecord
        records = model.objects.filter(name=score.name, district=score.district, cycle=cycle, formulation__in=query)
        return records


class WarehouseFulfillmentDataSource(ClosingBalanceMatchesOpeningBalanceDataSource):
    check = BalancesMatchCheck({}, {})

    def get_template(self, test):
        return "check/differentOrdersOverTime.html"

    def get_context(self, score, test, combination):
        current_cycle = score.cycle
        prev_cycle = get_prev_cycle(current_cycle)
        return {
            "main_title": "RAW ORDER DATA",
            "previous_cycle": self.get_table_for_cycle(prev_cycle, self.check, combination, score, [PACKS_ORDERED]),
            "current_cycle": self.get_table_for_cycle(current_cycle, self.check, combination, score, [QUANTITY_RECEIVED]),
        }


class GuidelineAdherenceDataSource(CheckDataSource):
    def get_template(self, test):
        return "check/adherence.html"

    checks = {
        GUIDELINE_ADHERENCE_ADULT_1L: {DF1: "TDF-based regimens", DF2: "AZT-based regimens", "check": GuidelineAdherenceCheckAdult1L},
        GUIDELINE_ADHERENCE_ADULT_2L: {DF1: "ATV/r-based regimens", DF2: "LPV/r-based regimens", "check": GuidelineAdherenceCheckAdult2L},
        GUIDELINE_ADHERENCE_PAED_1L: {DF1: "ABC-based regimens", DF2: "AZT-based regimens", "check": GuidelineAdherenceCheckPaed1L},
    }

    def get_context(self, score, test, combination):
        check_data = self.checks.get(test)
        check = check_data.get("check")({})
        check_combination = check.combinations[0]
        data = {"main_title": "RAW ORDER DATA", "tables": []}
        for part in [DF1, DF2]:
            field_names = [FIELD_NAMES.get(f) for f in check_combination.get(FIELDS)]
            table = {"name": check_data.get(part), "rows": [], "headers": field_names}
            formulation_query = check_combination.get(part)
            consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__in=formulation_query)
            totals = defaultdict(int)
            for record in consumption_records:
                row = {"column": record.formulation}
                sum = 0
                for field in check_combination.get(FIELDS):
                    value = getattr(record, field)
                    sum += int(value)
                    header = FIELD_NAMES.get(field)
                    row[header] = value
                    totals[header] += int(value)
                row["sum"] = sum
                totals["sum"] += sum
                table["rows"].append(row)
            table["totals"] = totals
            data["tables"].append(table)
        return data
