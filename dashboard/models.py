from custom_user.models import AbstractEmailUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from xlrd import open_workbook

from locations.models import Location


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
    total_quantity_to_be_ordered = models.FloatField(null=True, blank=True)
    notes = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.drug_formulation)


class WaosFile():
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
