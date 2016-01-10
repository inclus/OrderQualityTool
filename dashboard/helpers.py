import arrow
from arrow import Arrow, now


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


def to_date(text):
    month = text.split('-')[1].strip()
    return arrow.get(month, 'MMM YYYY')


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
        if page:
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


# checks
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
CONSUMPTION = 'consumption'
MULTIPLE_ORDERS = "MULTIPLE_ORDERS"
NNRTI_NEW_PAED = "nnrtiNewPaed"
NNRTI_NEW_ADULTS = "nnrtiNewAdults"
NNRTI_CURRENT_PAED = "nnrtiCurrentPaed"
NNRTI_CURRENT_ADULTS = "nnrtiCurrentAdults"

ADULT = 'adult'
PAED = 'paed'

# combinations
DEFAULT = 'DEFAULT'
F3 = "EFV200 (Paed)"
F2 = "ABC/3TC (Paed)"
F1 = "TDF/3TC/EFV (Adult)"

MULTIPLE = 'Multiple'
WEB_PAPER = 'Web/Paper'
DISTRICT = 'District'
WAREHOUSE = 'Warehouse'
IP = 'IP'
STATUS = 'status'
NAME = 'name'
SCORES = 'scores'
CS = 'cs'
ADS = 'ads'
PDS = 'pds'
LOCS = 'locs'

IS_ADULT = "IS_ADULT"
FORMULATION = 'formulation'
LOCATION = "Facility Index"
FIELDS = "fields"
MODEL = 'model'
RATIO = "ratio"
PATIENT_QUERY = "patient_query"
CONSUMPTION_QUERY = "consumption_query"
SUM = 'sum'
F1_QUERY = "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"
F3_QUERY = "Efavirenz (EFV) 200mg [Pack 90]"
F2_QUERY = "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"
ADULT_2L = "Adult 2L"
PAED_1L = "Paed 1L"
ADULT_1L = "Adult 1L"
DF2 = "data_field_2"
DF1 = "data_field_1"

# Scores
YES = "YES"
NO = "NO"
NOT_REPORTING = "NOT_REPORTING"

# Field Names
EXISTING = 'existing'
NEW = 'new'
PACKS_ORDERED = 'packs_ordered'
ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN = 'estimated_number_of_new_pregnant_women'
ESTIMATED_NUMBER_OF_NEW_PATIENTS = 'estimated_number_of_new_patients'
QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS = 'quantity_required_for_current_patients'
MONTHS_OF_STOCK_OF_HAND = 'months_of_stock_of_hand'
CLOSING_BALANCE = 'closing_balance'
LOSES_ADJUSTMENTS = 'loses_adjustments'
ART_CONSUMPTION = 'art_consumption'
PMTCT_CONSUMPTION = 'pmtct_consumption'
QUANTITY_RECEIVED = 'quantity_received'
OPENING_BALANCE = 'opening_balance'

# Sheet Names
CONSUMPTION_SHEET = 'CONSUMPTION'
PATIENTS_ADULT_SHEET = "PATIENTS (ADULT)"
PATIENTS_PAED_SHEET = "PATIENTS (PAED)"
