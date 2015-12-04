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


ORDER_FORM_FREE_OF_GAPS = "OrderFormFreeOfGaps"
QUANTITY_TO_BE_ORDERED = 'total_quantity_to_be_ordered'
OF_NEW_PREGNANT_WOMEN = 'estimated_number_of_new_pregnant_women'
NUMBER_OF_NEW_PATIENTS = 'estimated_number_of_new_patients'
FOR_CURRENT_PATIENTS = 'quantity_required_for_current_patients'
MONTHS_OF_STOCK_OF_HAND = 'months_of_stock_of_hand'
CLOSING_BALANCE = 'closing_balance'
LOSES_ADJUSTMENTS = 'loses_adjustments'
ART_CONSUMPTION = 'art_consumption'
PMTCT_CONSUMPTION = 'pmtct_consumption'
QUANTITY_RECEIVED = 'quantity_received'
OPENING_BALANCE = 'opening_balance'
ADULT = 'adult'
CONSUMPTION = 'consumption'
PAED = 'paed'
PATIENTS_ADULT = "PATIENTS (ADULT)"
PATIENTS_PAED = "PATIENTS (PAED)"