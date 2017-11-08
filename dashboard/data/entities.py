import attr

TABLE_COLUMN_NEW_PREGNANT_PATIENTS = "ESTIMATED NUMBER OF NEW HIV+ PREGNANT WOMEN"
TABLE_COLUMN_NEW_PATIENTS = "ESTIMATED NUMBER OF NEW ART PATIENTS"
TABLE_COLUMN_QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS = "QUANTITY REQUIRED FOR CURRENT PATIENTS"
TABLE_COLUMN_PACKS_ORDERED = "Packs Ordered"
TABLE_COLUMN_MONTHS_OF_STOCK_ON_HAND = "MONTHS OF STOCK ON-HAND"
TABLE_COLUMN_RECEIVED = "Quantity Recieved"
EXISTING = 'existing'
NEW = 'new'
TABLE_COLUMN_SUBCOUNTY = "Subcounty"
TABLE_COLUMN_REGION = "Region"
TABLE_COLUMN_FACILITY = "Facility"
TABLE_COLUMN_DISTRICT = "District"
TABLE_COLUMN_REGIMEN = "Regimen"
TABLE_COLUMN_OPENING_BALANCE = "Opening Balance"
TABLE_COLUMN_CLOSING_BALANCE = "Closing Balance"
TABLE_COLUMN_ART_CONSUMPTION = "ART Consumption"
TABLE_COLUMN_LOSES_ADJUSTMENTS = "Losses/Adjustments"
TABLE_COLUMN_NEW = "New"
TABLE_COLUMN_EXISTING = "Existing"


@attr.s(cmp=True, frozen=True)
class Location(object):
    facility = attr.ib()
    district = attr.ib()
    partner = attr.ib()
    warehouse = attr.ib()


@attr.s(cmp=True, frozen=True)
class RegimenLocationCombination(object):
    location = attr.ib()
    regimen = attr.ib()


@attr.s(cmp=True)
class Record(object):
    regimen = attr.ib()
    location = attr.ib()
    regimen_location = attr.ib()


@attr.s(cmp=True)
class PatientRecord(Record):
    existing = attr.ib()
    new = attr.ib()

    def add(self, record):
        return PatientRecord(
            location=self.location,
            regimen_location=self.regimen_location,
            existing=as_int(record.existing) + as_int(self.existing),
            new=as_int(record.new) + as_int(self.new),
            regimen=self.regimen)


def as_int(value):
    try:
        return int(value)
    except ValueError:
        return 0


@attr.s(cmp=True)
class ConsumptionRecord(Record):
    opening_balance = attr.ib()
    quantity_received = attr.ib()
    consumption = attr.ib()
    loses_adjustments = attr.ib()
    closing_balance = attr.ib()
    months_of_stock_on_hand = attr.ib()
    quantity_required_for_current_patients = attr.ib()
    number_of_new_art_patients = attr.ib()
    number_of_new_pregnant_women = attr.ib()
    packs_ordered = attr.ib()

    def add(self, record):
        opening_balance = as_int(self.opening_balance) + as_int(record.opening_balance)
        quantity_received = as_int(self.quantity_received) + as_int(record.quantity_received)
        consumption = as_int(self.consumption) + as_int(record.consumption)
        loses_adjustments = as_int(self.loses_adjustments) + as_int(record.loses_adjustments)
        closing_balance = as_int(self.closing_balance) + as_int(record.closing_balance)
        months_of_stock_on_hand = as_int(self.months_of_stock_on_hand) + as_int(record.months_of_stock_on_hand)
        quantity_required_for_current_patients = as_int(self.quantity_required_for_current_patients) + as_int(
            record.quantity_required_for_current_patients)
        number_of_new_art_patients = as_int(self.number_of_new_art_patients) + as_int(record.number_of_new_art_patients)
        number_of_new_pregnant_women = as_int(self.number_of_new_pregnant_women) + as_int(
            record.number_of_new_pregnant_women)
        packs_ordered = as_int(self.packs_ordered) + as_int(record.packs_ordered)
        return ConsumptionRecord(
            location=self.location,
            regimen_location=self.regimen_location,
            regimen=self.regimen,
            opening_balance=opening_balance,
            quantity_received=quantity_received,
            consumption=consumption,
            loses_adjustments=loses_adjustments,
            closing_balance=closing_balance,
            months_of_stock_on_hand=months_of_stock_on_hand,
            quantity_required_for_current_patients=quantity_required_for_current_patients,
            number_of_new_art_patients=number_of_new_art_patients,
            number_of_new_pregnant_women=number_of_new_pregnant_women,
            packs_ordered=packs_ordered,
        )


@attr.s
class DataImportRecord(object):
    warehouse = attr.ib()
    report_type = attr.ib()
    data = attr.ib()
    location = attr.ib(None)

    def get_facility(self):
        return self.data.get(TABLE_COLUMN_FACILITY)

    def get_region(self):
        return self.data.get(TABLE_COLUMN_REGION)

    def get_subcounty(self):
        return self.data.get(TABLE_COLUMN_SUBCOUNTY)

    def get_district(self):
        return self.data.get(TABLE_COLUMN_DISTRICT)

    def get_opening_balance(self):
        return self.data.get(TABLE_COLUMN_OPENING_BALANCE)

    def get_quantity_received(self):
        return self.data.get(TABLE_COLUMN_RECEIVED)

    def get_consumption(self):
        return self.data.get(TABLE_COLUMN_ART_CONSUMPTION)

    def get_loses_adjustments(self):
        return self.data.get(TABLE_COLUMN_LOSES_ADJUSTMENTS)

    def get_closing_balance(self):
        return self.data.get(TABLE_COLUMN_CLOSING_BALANCE)

    def get_months_of_stock_on_hand(self):
        return self.data.get(TABLE_COLUMN_MONTHS_OF_STOCK_ON_HAND)

    def get_quantity_required_for_current_patients(self):
        return self.data.get(TABLE_COLUMN_QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS)

    def get_number_of_new_art_patients(self):
        return self.data.get(TABLE_COLUMN_NEW_PATIENTS)

    def get_number_of_new_pregnant_patients(self):
        return self.data.get(TABLE_COLUMN_NEW_PREGNANT_PATIENTS)

    def get_packs_ordered(self):
        return self.data.get(TABLE_COLUMN_PACKS_ORDERED)

    def has_facility_without_region(self):
        return TABLE_COLUMN_REGION not in self.data and TABLE_COLUMN_FACILITY in self.data

    def build_location(self, partner_mapping):
        facility = self.get_facility()
        subcounty = self.get_subcounty()
        district = self.get_district()
        region = self.get_region()

        if self.has_facility_without_region():
            location_spread = self.get_facility().split("/")
            if len(location_spread) > 5:
                facility = location_spread[5]
                subcounty = location_spread[4]
                district = location_spread[3]
                region = location_spread[2]
        partner = partner_mapping.get(facility, None)
        return Location(
            facility=facility,
            district=district,
            partner=partner,
            warehouse=self.warehouse
        )

    def build_patient_record(self):
        regimen = self.data.get(TABLE_COLUMN_REGIMEN)
        rl = RegimenLocationCombination(location=self.location, regimen=regimen)
        return PatientRecord(location=self.location,
                             regimen_location=rl,
                             existing=self.data.get(TABLE_COLUMN_EXISTING),
                             new=self.data.get(TABLE_COLUMN_NEW),
                             regimen=regimen)

    def build_consumption_record(self):
        regimen = self.data.get("REGIMEN")
        rl = RegimenLocationCombination(location=self.location, regimen=regimen)
        return ConsumptionRecord(location=self.location,
                                 regimen_location=rl,
                                 opening_balance=self.get_opening_balance(),
                                 quantity_received=self.get_quantity_received(),
                                 consumption=self.get_consumption(),
                                 loses_adjustments=self.get_loses_adjustments(),
                                 closing_balance=self.get_closing_balance(),
                                 months_of_stock_on_hand=self.get_months_of_stock_on_hand(),
                                 quantity_required_for_current_patients=self.get_quantity_required_for_current_patients(),
                                 number_of_new_art_patients=self.get_number_of_new_art_patients(),
                                 number_of_new_pregnant_women=self.get_number_of_new_pregnant_patients(),
                                 packs_ordered=self.get_packs_ordered(),
                                 regimen=regimen)


@attr.s
class ReportOutput(object):
    report = attr.ib()
    output = attr.ib()
