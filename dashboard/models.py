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
    access_level = CharField(
            choices=((WAREHOUSE, WAREHOUSE), (DISTRICT, DISTRICT), (IIP, IIP), (MOH_CENTRAL, MOH_CENTRAL)), max_length=50)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    class Meta:
        app_label = 'dashboard'


class CycleScore(models.Model):
    cycle = models.CharField(max_length=256)
    test = models.CharField(max_length=256)
    yes = models.FloatField(null=True)
    no = models.FloatField(null=True)
    not_reporting = models.FloatField(null=True)

    class Meta:
        unique_together = ("cycle", "test")

    def __unicode__(self):
        return "%s %s YES:%s NO:%s NOT_REPORTING:%s" % (self.cycle, self.test, self.yes, self.no, self.not_reporting)


class CycleFormulationScore(models.Model):
    cycle = models.CharField(max_length=256)
    test = models.CharField(max_length=256)
    yes = models.FloatField(null=True)
    no = models.FloatField(null=True)
    not_reporting = models.FloatField(null=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        unique_together = ("cycle", "formulation", "test")

    def __unicode__(self):
        return "%s %s YES:%s NO:%s NOT_REPORTING:%s FORMULATION:%s" % (
            self.cycle, self.test, self.yes, self.no, self.not_reporting, self.formulation)


class Cycle(models.Model):
    facility = models.ForeignKey(Facility, related_name="records")
    cycle = models.CharField(max_length=256, db_index=True)
    reporting_status = models.BooleanField(default=False)
    web_based = models.BooleanField(default=False)
    multiple = models.BooleanField(default=False)

    class Meta:
        unique_together = ("cycle", "facility")

    def __unicode__(self):
        return "%s %s" % (self.facility, self.cycle)


choices = ((YES, YES), (NO, NO), (NOT_REPORTING, NOT_REPORTING))


class Score(models.Model):
    name = models.CharField(max_length=256)
    cycle = models.CharField(max_length=256)
    test = models.CharField(max_length=256)
    district = models.CharField(max_length=256)
    ip = models.CharField(max_length=256)
    warehouse = models.CharField(max_length=256)
    formulation = models.CharField(max_length=256, null=True)
    nnrtiNewPaed = models.CharField(choices=choices, max_length=20)
    stablePatientVolumes = models.CharField(choices=choices, max_length=20)
    REPORTING = models.CharField(choices=choices, max_length=20)
    consumptionAndPatients = models.CharField(choices=choices, max_length=20)
    nnrtiCurrentPaed = models.CharField(choices=choices, max_length=20)
    warehouseFulfilment = models.CharField(choices=choices, max_length=20)
    differentOrdersOverTime = models.CharField(choices=choices, max_length=20)
    closingBalanceMatchesOpeningBalance = models.CharField(choices=choices, max_length=20)
    WEB_BASED = models.CharField(choices=choices, max_length=20)
    OrderFormFreeOfGaps = models.CharField(choices=choices, max_length=20)
    MULTIPLE_ORDERS = models.CharField(choices=choices, max_length=20)
    nnrtiNewAdults = models.CharField(choices=choices, max_length=20)
    orderFormFreeOfNegativeNumbers = models.CharField(choices=choices, max_length=20)
    nnrtiCurrentAdults = models.CharField(choices=choices, max_length=20)
    stableConsumption = models.CharField(choices=choices, max_length=20)
    guidelineAdherenceAdult1L = models.CharField(choices=choices, max_length=20)
    guidelineAdherenceAdult2L = models.CharField(choices=choices, max_length=20)
    guidelineAdherencePaed1L = models.CharField(choices=choices, max_length=20)
    pass_count = models.IntegerField()
    fail_count = models.IntegerField()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        fields = ["nnrtiNewPaed",
                  "stablePatientVolumes",
                  "REPORTING",
                  "consumptionAndPatients",
                  "nnrtiCurrentPaed",
                  "warehouseFulfilment",
                  "differentOrdersOverTime",
                  "closingBalanceMatchesOpeningBalance",
                  "WEB_BASED",
                  "OrderFormFreeOfGaps",
                  "MULTIPLE_ORDERS",
                  "nnrtiNewAdults",
                  "orderFormFreeOfNegativeNumbers",
                  "nnrtiCurrentAdults",
                  "stableConsumption",
                  "guidelineAdherenceAdult1L",
                  "guidelineAdherenceAdult2L",
                  "guidelineAdherencePaed1L"
                  ]
        self.pass_count = 0
        self.fail_count = 0
        for field in fields:
            if getattr(self, field) == YES:
                self.pass_count += 1
            else:
                self.fail_count += 1

        super(Score, self).save(force_insert, force_update, using, update_fields)

    class Meta:
        unique_together = ("name", "cycle", "test", "formulation")


class Consumption(models.Model):
    facility_cycle = models.ForeignKey(Cycle, related_name="consumption")
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
    formulation = models.CharField(max_length=256, null=True, blank=True, db_index=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.formulation)


class AdultPatientsRecord(models.Model):
    facility_cycle = models.ForeignKey(Cycle, related_name="ads")
    existing = models.FloatField(null=True, blank=True)
    new = models.FloatField(null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.formulation)


class PAEDPatientsRecord(models.Model):
    facility_cycle = models.ForeignKey(Cycle, related_name="pds")
    existing = models.FloatField(null=True, blank=True)
    new = models.FloatField(null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.facility_cycle, self.formulation)
