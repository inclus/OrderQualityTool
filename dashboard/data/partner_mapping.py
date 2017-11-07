from openpyxl import load_workbook


def load_file(mapping_file):
    workbook = load_workbook(mapping_file, read_only=True, use_iterators=True)
    only_sheet = workbook.get_active_sheet()
    mapping = dict()
    for row in only_sheet.iter_rows(
                    'A%s:E%s' % (only_sheet.min_row + 1, only_sheet.max_row)):
        mapping[row[1].value] = row[3].value
    return mapping
