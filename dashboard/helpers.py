import arrow
from arrow import Arrow, now

NNRTI_NEW_PAED = "nnrtiNewPaed"

NNRTI_NEW_ADULTS = "nnrtiNewAdults"

NNRTI_CURRENT_PAED = "nnrtiCurrentPaed"

NNRTI_CURRENT_ADULTS = "nnrtiCurrentAdults"


class CustomArrow(Arrow):
    @classmethod
    def _get_frames(cls, name):
        if name in cls._ATTRS:
            return name, '{0}s'.format(name), 1
        elif name in ['week', 'weeks']:
            return 'week', 'weeks', 1
        elif name in ['quarter', 'quarters']:
            return 'quarter', 'months', 3
        elif cls._has_custom_frame(name):
            frame, count = name.split("=")
            return frame, '{0}s'.format(frame), int(count)
        raise AttributeError()

    @classmethod
    def _has_custom_frame(cls, name):
        parts = name.split("=")
        return len(parts) == 2 and parts[0] in cls._ATTRS


def format_range(start, end):
    return "%s - %s %s" % (start.format('MMM'), end.format('MMM'), start.format('YYYY'))


def generate_cycles(start, end):
    if start.month % 2 == 0:
        start = start.replace(months=-1)
    return [format_range(s, e) for s, e in CustomArrow.span_range("month=2", start, end)]


def generate_choices():
    return [(s, s) for s in generate_cycles(now().replace(years=-2), now())]


ORDER_FORM_FREE_OF_GAPS = "OrderFormFreeOfGaps"
ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS = "orderFormFreeOfNegativeNumbers"
DIFFERENT_ORDERS_OVER_TIME = "differentOrdersOverTime"
CLOSING_BALANCE_MATCHES_OPENING_BALANCE = "closingBalanceMatchesOpeningBalance"
CONSUMPTION_AND_PATIENTS = "consumptionAndPatients"
STABLE_CONSUMPTION = "stableConsumption"
WAREHOUSE_FULFILMENT = "warehouseFulfilment"
STABLE_PATIENT_VOLUMES = "stablePatientVolumes"
GUIDELINE_ADHERENCE = "guidelineAdherence"
REPORTING = "REPORTING"
WEB_BASED = "WEB_BASED"
ADULT = 'adult'
CONSUMPTION = 'consumption'
PAED = 'paed'
PATIENTS_ADULT = "PATIENTS (ADULT)"
PATIENTS_PAED = "PATIENTS (PAED)"
MULTIPLE_ORDERS = "MULTIPLE_ORDERS"
YES = "YES"
NO = "NO"
NOT_REPORTING = "NOT_REPORTING"


def to_date(text):
    month = text.split('-')[1].strip()
    return arrow.get(month, 'MMM YYYY')


F3 = "EFV200 (Paed)"
F2 = "ABC/3TC (Paed)"
F1 = "TDF/3TC/EFV (Adult)"


def sort_cycle(item1, item2):
    if to_date(item1) < to_date(item2):
        return -1
    elif to_date(item1) > to_date(item2):
        return 1
    else:
        return 0


class Pager(object):
    def __init__(self, data, page=1, page_count=20):
        self.data = data
        if page and page > 0:
            self.page = int(page)
        else:
            self.page = 1

        if page_count:
            self.page_count = int(page_count)
        else:
            self.page_count = 20

    def get_data(self):
        offset = (self.page - 1) * self.page_count
        end = offset + self.page_count
        s = slice(offset, end)
        return self.data[s]