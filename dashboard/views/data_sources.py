from collections import defaultdict

import pydash

from dashboard.data.adherence import GuidelineAdherenceCheckAdult1L, GuidelineAdherenceCheckAdult2L, GuidelineAdherenceCheckPaed1L
from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.cycles import OrdersOverTimeCheck, BalancesMatchCheck, StableConsumptionCheck, StablePatientVolumesCheck
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.data.nn import NNRTINEWPAEDCheck, NNRTINewAdultsCheck, NNRTICURRENTADULTSCheck, NNRTICURRENTPAEDCheck
from dashboard.helpers import *
from dashboard.models import Consumption, AdultPatientsRecord, PAEDPatientsRecord

CHECK = "check"
IS_HEADER = "isHeader"
HEADERS = "headers"
RESULTS_TITLE = "results_title"
query_map = {F1: F1_QUERY, F2: F2_QUERY, F3: F3_QUERY}


def get_combination(combinations, name):
    return pydash.select(combinations, lambda x: x[NAME] == name)[0]


def get_int(value):
    try:
        return int(value), True
    except (ValueError, TypeError):
        if value is None:
            return "", False
        return value, False


class CheckDataSource(object):
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

    def as_array(self, score, test, combination):
        row = []
        data = self.get_context(score, test, combination)
        result = getattr(score, test, None)
        name_row = ["", TEST_NAMES.get(test, None)]
        row.append([""])
        row.append(name_row)
        row.append([""])
        row.append(["", "Facility", "District", "Warehouse", "IP", "Cycle", "Result"])
        row.append(["", score.name, score.district, score.warehouse, score.ip, score.cycle, get_actual_result(result, combination)])
        row.append([""])
        row.append([""])
        row.append(["", data["main_title"]])
        return row


def get_negatives_data(score, test, combination):
    check = NegativeNumbersQualityCheck({})
    formulation_query = query_map.get(combination)
    consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__icontains=formulation_query)
    tables = []
    for consumption in consumption_records:
        formulation_data = {NAME: consumption.formulation}
        records = []
        for field in check.fields:
            raw_value, valid = get_int(getattr(consumption, field))
            records.append({COLUMN: FIELD_NAMES.get(field), VALUE: raw_value})
        formulation_data['records'] = records
        tables.append(formulation_data)
    return {"main_title": "RAW ORDER DATA", "formulations": tables}


class NegativesCheckDataSource(CheckDataSource):
    def get_context(self, score, test, combination):
        return get_negatives_data(score, test, combination)

    def as_array(self, score, test, combination):
        row = super(NegativesCheckDataSource, self).as_array(score, test, combination)
        data = self.get_context(score, test, combination)
        for formulation in data.get("formulations", []):
            row.append(["", formulation["name"]])
            for record in formulation["records"]:
                row.append(["", record["column"], record["value"]])
        return row


def values_for_models(fields, models):
    output = []
    for obj in models:
        for field in fields:
            value = getattr(obj, field)
            output.append(value)
    return output


def append_values_for_header(consumption, header_row, n, no_consumption_tables, records_key='records'):
    records = []
    records_count = 0
    if n < no_consumption_tables:
        name = consumption[n].get('name')
        header_row.append(name)
        header_row.append("")
        records = consumption[n].get(records_key, [])
        records_count = len(records)
    else:
        header_row.append("")
        header_row.append("")
    return records, records_count


def append_values_for_row(records, current_row, records_count, record_index):
    if record_index < records_count:
        consumption_record = records[record_index]
        current_row.append(consumption_record.get(COLUMN))
        current_row.append(consumption_record.get(VALUE))
    else:
        current_row.append("")
        current_row.append("")


def calculate_packs(check_combination):
    packs = [{COLUMN: check_combination.get(CONSUMPTION_QUERY), VALUE: check_combination.get(RATIO)}]
    return packs


def calculate_consumption_totals(check_combination, consumption_records):
    totals = []
    total = 0
    for consumption in consumption_records:
        entry = {COLUMN: consumption.formulation}
        values = values_for_models(check_combination.get(FIELDS, []), [consumption])
        caluclated_sum = pydash.chain(values).reject(lambda x: x is None).sum().value()
        reduced_sum = caluclated_sum / check_combination[RATIO]
        entry[VALUE] = reduced_sum
        total += reduced_sum
        totals.append(entry)
    totals.append({COLUMN: TOTAL, VALUE: total, IS_HEADER: True})
    return totals


def calculate_consumption_tables(check_combination, consumption_records):
    tables = []
    for consumption in consumption_records:
        formulation_data = {NAME: consumption.formulation}
        records = []
        calculated_sum = 0
        for field in check_combination.get(FIELDS, []):
            int_value, valid_int = get_int(getattr(consumption, field))
            if valid_int:
                calculated_sum += int_value
            records.append({COLUMN: FIELD_NAMES.get(field), VALUE: int_value})
        records.append({COLUMN: TOTAL, VALUE: calculated_sum, IS_HEADER: True})

        formulation_data['records'] = records
        tables.append(formulation_data)
    return tables


def calculate_patient_tables(patient_records):
    patient_tables = []
    for pr in patient_records:
        formulation_data = {NAME: pr.formulation}
        records = []
        calculated_sum = 0
        for field in [NEW, EXISTING]:
            int_value, valid_int = get_int(getattr(pr, field))
            if valid_int:
                calculated_sum += int(int_value)
            records.append({COLUMN: FIELD_NAMES.get(field), VALUE: int_value})
        records.append({COLUMN: TOTAL, VALUE: calculated_sum, IS_HEADER: True})
        formulation_data['records'] = records
        patient_tables.append(formulation_data)
    return patient_tables


def calculate_patient_totals(patient_records):
    patient_totals = []
    total = 0
    for pr in patient_records:
        entry = {COLUMN: pr.formulation}
        values = values_for_models([NEW, EXISTING], [pr])
        sum = pydash.chain(values).reject(lambda x: x is None).sum().value()
        entry[VALUE] = sum
        total += int(sum)
        patient_totals.append(entry)
    patient_totals.append({COLUMN: TOTAL, VALUE: total, IS_HEADER: True})
    return patient_totals


def get_consumption_and_patients(score, test, combination_name):
    check = ConsumptionAndPatientsQualityCheck({})
    check_combination = get_combination(check.combinations, combination_name)
    formulation_query = check_combination.get(CONSUMPTION_QUERY)
    consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__icontains=formulation_query)
    model = AdultPatientsRecord if check_combination.get(IS_ADULT, False) else PAEDPatientsRecord
    patient_records = model.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__in=check_combination.get(PATIENT_QUERY))

    return {
        "main_title": "RAW ORDER DATA",
        "consumption": (calculate_consumption_tables(check_combination, consumption_records)),
        "patients": (calculate_patient_tables(patient_records)),
        "packs": (calculate_packs(check_combination)),
        "patient_totals": (calculate_patient_totals(patient_records)),
        "consumption_totals": (calculate_consumption_totals(check_combination, consumption_records))
    }


def add_blank_column(header_row):
    header_row.append("")


def add_blank_row(row):
    row.append([])


class ConsumptionAndPatientsDataSource(CheckDataSource):
    def get_context(self, score, test, combination):
        return get_consumption_and_patients(score, test, combination)

    def as_array(self, score, test, combination):
        row = super(ConsumptionAndPatientsDataSource, self).as_array(score, test, combination)
        data = self.get_context(score, test, combination)
        row.append(["", "CONSUMPTION", "", "", "PATIENTS"])
        patients = data.get('patients', [])
        consumption = data.get('consumption', [])
        no_patient_tables = len(patients)
        no_consumption_tables = len(consumption)
        size = max(no_patient_tables, no_consumption_tables)
        for n in range(size):
            header_row = [""]

            consumption_records, no_consumption_records = append_values_for_header(consumption, header_row, n, no_consumption_tables)
            add_blank_column(header_row)
            patient_records, no_patient_records = append_values_for_header(patients, header_row, n, no_patient_tables)

            add_blank_row(row)
            row.append(header_row)

            i = max(no_patient_records, no_consumption_records)

            for record_index in range(i):
                current_row = [""]
                append_values_for_row(consumption_records, current_row, no_consumption_records, record_index)
                add_blank_column(current_row)
                append_values_for_row(patient_records, current_row, no_patient_records, record_index)
                row.append(current_row)

        add_blank_row(row)
        add_blank_row(row)
        row.append(["", "Conversion Ratio (packs per patient, bimonthly)"])
        for pack in data.get('packs', []):
            row.append(["", pack.get(COLUMN), pack.get(VALUE)])

        add_blank_row(row)
        add_blank_row(row)
        row.append(["", "ESTIMATED CURRENT PATIENTS"])
        row.append(["", "From Consumption Data", "", "", "From Patient Data"])
        patient_totals = data.get('patient_totals', [])
        consumption_totals = data.get('consumption_totals', [])
        no_patient_totals = len(patient_totals)
        no_consumption_totals = len(consumption_totals)
        row_count = max(no_patient_totals, no_consumption_totals)
        for record_index in range(row_count):
            current_row = [""]
            append_values_for_row(consumption_totals, current_row, no_consumption_totals, record_index)
            add_blank_column(current_row)
            append_values_for_row(patient_totals, current_row, no_patient_totals, record_index)
            row.append(current_row)
        return row


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
        tables[0][ROWS] = self.build_rows(check, records)
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
                rows.append({COLUMN: FIELD_NAMES.get(field), VALUE: value})
        return rows


def get_table_for_cycle(cycle, check, combination, score, fields):
    check_combination = get_combination(check.combinations, combination)
    formulation_query = check_combination.get(CONSUMPTION_QUERY)
    consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=cycle, formulation__icontains=formulation_query)
    tables = [
        {"cycle": cycle}
    ]
    rows = []
    for consumption in consumption_records:
        for field in fields:
            int_value, valid_int = get_int(getattr(consumption, field))
            rows.append({COLUMN: FIELD_NAMES.get(field), VALUE: int_value})
    tables[0][ROWS] = rows
    return tables


class ClosingBalanceMatchesOpeningBalanceDataSource(CheckDataSource):
    check = BalancesMatchCheck({}, {})

    def get_template(self, test):
        return "check/differentOrdersOverTime.html"

    def get_context(self, score, test, combination):
        current_cycle = score.cycle
        prev_cycle = get_prev_cycle(current_cycle)
        return {
            "main_title": "RAW ORDER DATA",
            "previous_cycle": get_table_for_cycle(prev_cycle, self.check, combination, score, [CLOSING_BALANCE]),
            "current_cycle": get_table_for_cycle(current_cycle, self.check, combination, score, [OPENING_BALANCE]),
        }


class StableConsumptionDataSource(TwoCycleDataSource):
    check = StableConsumptionCheck({}, {})

    def get_template(self, test):
        return "check/differentOrdersOverTime.html"

    def build_rows(self, check, consumption_records):
        rows = []

        for consumption in consumption_records:
            tot = 0
            for field in check.fields:
                int_value, valid_int = get_int(getattr(consumption, field))
                if valid_int:
                    tot += int_value
                rows.append({COLUMN: FIELD_NAMES.get(field), VALUE: int_value})
            rows.append({COLUMN: TOTAL, VALUE: tot, IS_HEADER: True})
        return rows


class StablePatientVolumesDataSource(TwoCycleDataSource):
    def get_template(self, test):
        return "check/patientStability.html"

    check = StablePatientVolumesCheck({}, {})

    def get_table_for_cycle(self, cycle, check, combination, score):
        check_combination = get_combination(check.combinations, combination)
        records = self.get_queryset(check_combination, cycle, score)
        tables = [
            {"cycle": cycle}
        ]
        tables[0][ROWS], tables[0][HEADERS], tables[0]['totals'] = self.build_rows(check, records)
        return tables

    def build_rows(self, check, records):
        rows = []
        total = 0
        headers = [FIELD_NAMES.get(field) for field in check.fields]
        headers.append(TOTAL)
        totals = {}
        for field in headers:
            totals[field] = 0
        for consumption in records:
            row_total = 0
            row = {COLUMN: consumption.formulation}
            for field in check.fields:
                field_name = FIELD_NAMES.get(field)
                int_value, valid_int = get_int(getattr(consumption, field))
                if valid_int:
                    row_total += int_value
                    row[field_name] = int_value
                    totals[field_name] += int_value
            row[TOTAL] = row_total
            totals[TOTAL] += row_total
            rows.append(row)
            total += row_total
        return rows, headers, totals

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
            "previous_cycle": get_table_for_cycle(prev_cycle, self.check, combination, score, [PACKS_ORDERED]),
            "current_cycle": get_table_for_cycle(current_cycle, self.check, combination, score, [QUANTITY_RECEIVED]),
        }


class GuidelineAdherenceDataSource(CheckDataSource):
    def get_template(self, test):
        return "check/adherence.html"

    checks = {
        GUIDELINE_ADHERENCE_ADULT_1L: {RESULTS_TITLE: "TDF Based as % of the Total", DF1: "TDF-based regimens", DF2: "AZT-based regimens", CHECK: GuidelineAdherenceCheckAdult1L},
        GUIDELINE_ADHERENCE_ADULT_2L: {RESULTS_TITLE: "ATV/r Based as % of the Total", DF1: "ATV/r-based regimens", DF2: "LPV/r-based regimens", CHECK: GuidelineAdherenceCheckAdult2L},
        GUIDELINE_ADHERENCE_PAED_1L: {RESULTS_TITLE: "ABC Based as % of the Total", DF1: "ABC-based regimens", DF2: "AZT-based regimens", CHECK: GuidelineAdherenceCheckPaed1L},
    }

    def get_context(self, score, test, combination):
        check_data = self.checks.get(test)
        check = check_data.get(CHECK)({})
        check_combination = check.combinations[0]
        data = {"main_title": "RAW ORDER DATA", "tables": []}
        data["result_title"] = check_data[RESULTS_TITLE]
        for part in [DF1, DF2]:
            field_names = [FIELD_NAMES.get(f) for f in check_combination.get(FIELDS)]
            table = {NAME: check_data.get(part), ROWS: [], HEADERS: field_names}
            formulation_query = check_combination.get(part)
            consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__in=formulation_query)
            totals = defaultdict(int)
            for record in consumption_records:
                row = {COLUMN: record.formulation}
                part_sum = 0
                for field in check_combination.get(FIELDS):
                    int_value, valid_int = get_int(getattr(record, field))
                    header = FIELD_NAMES.get(field)
                    if valid_int:
                        part_sum += int(int_value)
                        totals[header] += int(int_value)
                    row[header] = int_value
                row["sum"] = part_sum
                totals["sum"] += part_sum
                table[ROWS].append(row)
            table["totals"] = totals
            data["tables"].append(table)
        df1_sum = data["tables"][0]["totals"]["sum"]
        df2_sum = data["tables"][1]["totals"]["sum"]
        table_total = (df1_sum + df2_sum)
        if table_total == 0:
            score = 0
        else:
            score = (float(df1_sum) * 100) / float(table_total)
        data["score"] = score
        return data


def get_field_name(field):
    return FIELD_NAMES.get(field).replace("Consumption", "").strip()


class NNRTIDataSource(CheckDataSource):
    def get_template(self, test):
        return "check/nnrti.html"

    checks = {
        NNRTI_NEW_PAED: {CHECK: NNRTINEWPAEDCheck, "sub": "Estimated New Patients"},
        NNRTI_NEW_ADULTS: {CHECK: NNRTINewAdultsCheck, "sub": "Estimated New Patients"},
        NNRTI_CURRENT_ADULTS: {CHECK: NNRTICURRENTADULTSCheck, "sub": "Consumption"},
        NNRTI_CURRENT_PAED: {CHECK: NNRTICURRENTPAEDCheck, "sub": "Consumption"},
    }

    def get_context(self, score, test, combination):
        nnrti_titles = {DF1: "NRTI", DF2: "NNRTI/PI"}
        context = defaultdict(dict)
        context["main_title"] = "RAW ORDER DATA"
        sub_title = self.checks.get(test).get("sub")
        context["sub_title"] = sub_title
        check_config = self.checks.get(test).get(CHECK).combinations[0]

        has_other = OTHER in check_config
        for part in [DF1, DF2]:
            title = nnrti_titles.get(part)
            context[part][HEADERS] = []
            context[part]["table_header"] = title
            context[part][ROWS] = []
            ratio_key = "%s_ratios" % part
            calculated_key = "%s_calculated" % part
            context[ratio_key][ROWS] = []
            context[calculated_key][ROWS] = []
            check_fields = check_config.get(FIELDS)
            for field in check_fields:
                context[part][HEADERS].append(get_field_name(field))
            context[part][HEADERS].append(TOTAL)
            formulation_query = check_config[part]
            if has_other and part == DF2:
                formulation_query = check_config.get(OTHER) + formulation_query
            consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__in=formulation_query)
            part_total = 0
            for record in consumption_records:
                row = {COLUMN: record.formulation}

                row_sum = 0
                for field in check_fields:
                    int_value, valid_int = get_int(getattr(record, field))
                    if valid_int:
                        row_sum += int(int_value)
                    header = get_field_name(field)
                    row[header] = int_value
                row[TOTAL] = row_sum
                context[part][ROWS].append(row)
                combination_ratio = check_config.get(RATIO)
                if has_other and record.formulation in check_config.get(OTHER):
                    combination_ratio = 1.0
                ratio_row = {COLUMN: record.formulation, VALUE: combination_ratio}
                calculated_sum = row_sum / combination_ratio
                calculated_row = {COLUMN: record.formulation, VALUE: calculated_sum}
                context[ratio_key][ROWS].append(ratio_row)
                context[calculated_key][ROWS].append(calculated_row)
                part_total += calculated_sum
            context[calculated_key][ROWS].append({COLUMN: TOTAL, VALUE: part_total, IS_HEADER: True})

            context["%s_COUNT" % part] = part_total
        df1_total = context["%s_COUNT" % DF1]
        df2_total = context["%s_COUNT" % DF2]
        final_score = 0
        if df2_total > 0:
            final_score = abs(float((df2_total - df1_total) * 100) / df2_total)
        context['FINAL_SCORE'] = final_score
        context[SHOW_CONVERSION] = check_config.get(SHOW_CONVERSION)

        return context
