from custom_user.models import AbstractEmailUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from openpyxl import load_workbook
from xlrd import open_workbook

from locations.models import Location

CONSUMPTION = "CONSUMPTION"


class DashboardUser(AbstractEmailUser):
    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    location = models.ForeignKey(Location, null=True, blank=True)


class FacilityCycleRecord(models.Model):
    facility = models.ForeignKey(Location)
    cycle = models.CharField(max_length=256)

    def __unicode__(self):
        return "%s %s" % (self.facility, self.cycle)


class DrugFormulation(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    unit = models.CharField(max_length=256, null=False, blank=False)

    def __unicode__(self):
        return self.name


class FacilityConsumptionRecord(models.Model):
    facility_cycle = models.ForeignKey(FacilityCycleRecord)
    drug_formulation = models.ForeignKey(DrugFormulation)
    opening_balance = models.FloatField(null=True, blank=True)
    quantity_received = models.FloatField(null=True, blank=True)
    pmtct_consumption = models.FloatField(null=True, blank=True)
    art_consumption = models.FloatField(null=True, blank=True)
    loses_adjustments = models.FloatField(null=True, blank=True)
    closing_balance = models.FloatField(null=True, blank=True)
    months_of_stock_of_hand = models.FloatField(null=True, blank=True)
    quantity_required_for_current_patients = models.FloatField(null=True, blank=True)
    estimated_number_of_new_patients = models.FloatField(null=True, blank=True)
    estimated_number_of_new_pregnant_women = models.FloatField(null=True, blank=True)
    packs_ordered = models.FloatField(null=True, blank=True)
    total_quantity_to_be_ordered = models.FloatField(null=True, blank=True)
    notes = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.drug_formulation)


class WaosStandardReport():
    def __init__(self, path):
        self.path = path
        self.worksheet = self.load_worksheet()

    def load_worksheet(self):
        workbook = open_workbook(self.path)
        return workbook.sheet_by_index(0)

    def get_data(self):
        record = self.get_facility_record()
        if record:
            for n in range(4, 14):
                self.build_consumption_record(n, record)

            for n in range(16, 24):
                self.build_consumption_record(n, record)

            return record

    def build_consumption_record(self, n, record):
        formulation_name = self.worksheet.cell_value(n, 1)
        unit = self.worksheet.cell_value(n, 2)
        formulation, created = DrugFormulation.objects.get_or_create(name=formulation_name, unit=unit)
        consumption_record, created = FacilityConsumptionRecord.objects.get_or_create(facility_cycle=record, drug_formulation=formulation)
        consumption_record.opening_balance = self.get_numerical_value(n, 3)
        consumption_record.quantity_received = self.get_numerical_value(n, 4)
        consumption_record.pmtct_consumption = self.get_numerical_value(n, 5)
        consumption_record.art_consumption = self.get_numerical_value(n, 6)
        consumption_record.loses_adjustments = self.get_numerical_value(n, 7)
        consumption_record.closing_balance = self.get_numerical_value(n, 8)
        consumption_record.months_of_stock_of_hand = self.get_numerical_value(n, 9)
        consumption_record.quantity_required_for_current_patients = self.get_numerical_value(n, 10)
        consumption_record.estimated_number_of_new_patients = self.get_numerical_value(n, 11)
        consumption_record.estimated_number_of_new_pregnant_women = self.get_numerical_value(n, 12)
        consumption_record.total_quantity_to_be_ordered = self.get_numerical_value(n, 13)
        consumption_record.notes = self.worksheet.cell_value(n, 14)
        consumption_record.save()

    def get_numerical_value(self, n, i):
        value = self.worksheet.cell_value(n, i)
        if value:
            return value

    def get_facility_record(self):
        facility_name = self.worksheet.cell_value(27, 1)
        level = self.worksheet.cell_value(28, 1)
        full_name = "%s %s" % (facility_name, level)
        cycle = self.worksheet.cell_value(30, 1)
        try:
            location = Location.objects.get(name__icontains=full_name)
            record, exists = FacilityCycleRecord.objects.get_or_create(facility=location, cycle=cycle)
            return record
        except ObjectDoesNotExist:
            return None


class GeneralReport():
    def __init__(self, path, cycle):
        self.path = path
        self.cycle = cycle
        self.workbook = self.get_workbook()

    def get_workbook(self):
        return load_workbook(self.path)

    def get_facility_record(self, name):
        try:
            location = Location.objects.get(name__icontains=name)
            record, exists = FacilityCycleRecord.objects.get_or_create(facility=location, cycle=self.cycle)
            return record
        except ObjectDoesNotExist:
            return None

    def parse_row(self, row):
        facility_record = self.get_facility_record(row[0].value)
        formulation_name = row[1].value
        formulation, _ = DrugFormulation.objects.get_or_create(name=formulation_name)
        consumption_record, _ = FacilityConsumptionRecord.objects.get_or_create(facility_cycle=facility_record, drug_formulation=formulation)
        consumption_record.opening_balance = self.get_value(row, 3)
        consumption_record.quantity_received = self.get_value(row, 4)
        consumption_record.pmtct_consumption = self.get_value(row, 6)
        consumption_record.art_consumption = self.get_value(row, 5)
        consumption_record.loses_adjustments = self.get_value(row, 7)
        consumption_record.closing_balance = self.get_value(row, 8)
        consumption_record.months_of_stock_of_hand = self.get_value(row, 9)
        consumption_record.quantity_required_for_current_patients = self.get_value(row, 10)
        consumption_record.estimated_number_of_new_patients = self.get_value(row, 11)
        consumption_record.estimated_number_of_new_pregnant_women = self.get_value(row, 12)
        consumption_record.packs_ordered = self.get_value(row, 13)
        consumption_record.save()

    def get_value(self, row, i):
        value = row[i].value
        if value and value != "-":
            return row[i].value

    def get_data(self):
        consumption_sheet = self.workbook.get_sheet_by_name(CONSUMPTION)
        for row in consumption_sheet.iter_rows('A%s:W%s' % (consumption_sheet.min_row + 1, consumption_sheet.max_row)):
            self.parse_row(row)
