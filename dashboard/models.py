import logging

from custom_user.models import AbstractEmailUser
from django.db import models
from django.db.models import CharField

from dashboard.helpers import NOT_REPORTING, YES, NO
from locations.models import Facility

MOH_CENTRAL = "MOH CENTRAL"

IIP = "IP"

DISTRICT = "District"

WAREHOUSE = "Warehouse"

logger = logging.getLogger(__name__)
CONSUMPTION = "CONSUMPTION"
LOCATION = "Facility Index"


class DashboardUser(AbstractEmailUser):
    access_level = CharField(choices=((WAREHOUSE, WAREHOUSE), (DISTRICT, DISTRICT), (IIP, IIP), (MOH_CENTRAL, MOH_CENTRAL)), max_length=50)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    class Meta:
        app_label = 'dashboard'


class CycleTestScore(models.Model):
    cycle = models.CharField(max_length=256)
    test = models.CharField(max_length=256)
    yes = models.FloatField(null=True)
    no = models.FloatField(null=True)
    not_reporting = models.FloatField(null=True)

    class Meta:
        unique_together = ("cycle", "test")

    def __unicode__(self):
        return "%s %s YES:%s NO:%s NOT_REPORTING:%s" % (self.cycle, self.test, self.yes, self.no, self.not_reporting)


class CycleFormulationTestScore(models.Model):
    cycle = models.CharField(max_length=256)
    test = models.CharField(max_length=256)
    yes = models.FloatField(null=True)
    no = models.FloatField(null=True)
    not_reporting = models.FloatField(null=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        unique_together = ("cycle", "formulation", "test")

    def __unicode__(self):
        return "%s %s YES:%s NO:%s NOT_REPORTING:%s FORMULATION:%s" % (self.cycle, self.test, self.yes, self.no, self.not_reporting, self.formulation)


class FacilityCycleRecord(models.Model):
    facility = models.ForeignKey(Facility, related_name="records")
    cycle = models.CharField(max_length=256)
    reporting_status = models.BooleanField(default=False)
    web_based = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)

    class Meta:
        unique_together = ("cycle", "facility")

    def __unicode__(self):
        return "%s %s" % (self.facility, self.cycle)


class FacilityCycleRecordScore(models.Model):
    facility_cycle = models.ForeignKey(FacilityCycleRecord, related_name="scores")
    test = models.CharField(max_length=256)
    formulation = models.CharField(max_length=256, null=True)
    score = models.CharField(choices=((YES, YES), (NO, NO), (NOT_REPORTING, NOT_REPORTING)), db_index=True, max_length=20)

    class Meta:
        unique_together = ("facility_cycle", "formulation", "test")

    def __unicode__(self):
        return "%s %s %s" % (self.facility_cycle, self.test, self.score)


class FacilityConsumptionRecord(models.Model):
    facility_cycle = models.ForeignKey(FacilityCycleRecord)
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
    formulation = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.formulation)


class AdultPatientsRecord(models.Model):
    facility_cycle = models.ForeignKey(FacilityCycleRecord)
    existing = models.FloatField(null=True, blank=True)
    new = models.FloatField(null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.formulation)


class PAEDPatientsRecord(models.Model):
    facility_cycle = models.ForeignKey(FacilityCycleRecord)
    existing = models.FloatField(null=True, blank=True)
    new = models.FloatField(null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.formulation)
