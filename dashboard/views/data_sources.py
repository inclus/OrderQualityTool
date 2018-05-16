import pydash

from dashboard.helpers import *
from dashboard.models import Consumption

CHECK = "check"
IS_HEADER = "isHeader"
HEADERS = "headers"
RESULTS_TITLE = "results_title"
query_map = {F1: F1_QUERY, F2: F2_QUERY, F3: F3_QUERY}


def get_combination(combinations, name):
    return pydash.filter_(combinations, lambda x: x[NAME] == name)[0]


def get_int(value):
    try:
        return int(value), True
    except (ValueError, TypeError):
        if value is None:
            return "", False
        return value, False


class CheckDataSource(object):
    show_formulation = True

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
        result = score.data.get(test, None)
        name_row = ["", test]
        row.append([""])
        row.append(name_row)
        row.append([""])
        headers = ["", "Facility", "District", "Warehouse", "IP", "Cycle"]
        details = [
            "", score.name, score.district, score.warehouse, score.ip, score.cycle
        ]
        if self.show_formulation:
            headers.append("Formulation")
            details.append(combination)
        headers.append("Result")
        details.append(get_actual_result(result, combination))
        row.append(headers)
        row.append(details)
        row.append([""])
        row.append([""])
        row.append(["", data["main_title"]])
        return row


def values_for_models(fields, models):
    output = []
    for obj in models:
        for field in fields:
            value = getattr(obj, field)
            output.append(value)
    return output


def append_values_for_header(
    consumption, header_row, n, table_count, records_key="records", header_key="name"
):
    records = []
    records_count = 0
    if n < table_count:
        name = consumption[n].get(header_key)
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


def add_blank_column(header_row):
    header_row.append("")


def add_blank_row(row):
    row.append([])


def get_table_for_cycle(cycle, check, combination, score, fields):
    check_combination = get_combination(check.combinations, combination)
    formulation_query = check_combination.get(CONSUMPTION_QUERY)
    consumption_records = Consumption.objects.filter(
        name=score.name,
        district=score.district,
        cycle=cycle,
        formulation__icontains=formulation_query,
    )
    tables = [{"cycle": cycle}]
    rows = []
    for consumption in consumption_records:
        for field in fields:
            int_value, valid_int = get_int(getattr(consumption, field))
            rows.append({COLUMN: FIELD_NAMES.get(field), VALUE: int_value})
    tables[0][ROWS] = rows
    return tables


def build_dynamic_header(header_row, n, no_tables, tables):
    records = []
    table = []
    if n < no_tables:
        table = tables[n]
        records = table.get("rows", [])
        name = table.get("cycle")
        header_row.append(name)

        for header in table.get("headers"):
            header_row.append(header)
    return records, table


def append_values_for_headers(current_row, rows, table, line, has_sum=True):
    if line < len(rows):
        item = rows[line]
        current_row.append(item.get("column"))
        for header in table.get("headers"):
            current_row.append(item.get(header))
        if has_sum:
            current_row.append(item.get("sum"))
    else:
        current_row.append("")
        for header in table.get("headers"):
            current_row.append("")
        if has_sum:
            current_row.append("")


def append_total_row(table, totals, total_row):
    for header in table.get("headers"):
        total_row.append(totals.get(header))
    total_row.append(totals.get("sum"))


def get_field_name(field):
    return FIELD_NAMES.get(field).replace("Consumption", "").strip()
