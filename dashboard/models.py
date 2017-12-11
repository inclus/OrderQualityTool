import logging

from custom_user.models import AbstractEmailUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import CharField
from jsonfield import JSONField
from picklefield import PickledObjectField

from dashboard.data.partner_mapping import FormattedKeyDict
from dashboard.helpers import NOT_REPORTING, YES, NO, REPORT_TYPES
from dashboard.widget import TestDefinitionField

MOH_CENTRAL = "MOH CENTRAL"

IIP = "IP"

DISTRICT = "District"

WAREHOUSE = "Warehouse"

logger = logging.getLogger(__name__)
CONSUMPTION = "CONSUMPTION"
LOCATION = "Facility Index"
MAUL = "MAUL"
JMS = "JMS"
NMS = "NMS"

WAREHOUSES = ((MAUL, MAUL), (JMS, JMS), (NMS, NMS))


class DashboardUser(AbstractEmailUser):
    access_level = CharField(
        choices=(
            (WAREHOUSE, WAREHOUSE),
            (DISTRICT, DISTRICT),
            (IIP, IIP), (MOH_CENTRAL, MOH_CENTRAL)), max_length=50)
    access_area = CharField(max_length=250, null=True, blank=True)

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    class Meta:
        app_label = 'dashboard'
        verbose_name_plural = "Users"


class Cycle(models.Model):
    title = models.CharField(max_length=256, db_index=True, unique=True)
    state = PickledObjectField()

    def __unicode__(self):
        return "%s" % (self.title)


choices = ((YES, YES), (NO, NO), (NOT_REPORTING, NOT_REPORTING))


class Score(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    cycle = models.CharField(max_length=256, db_index=True)
    district = models.CharField(max_length=256, db_index=True)
    ip = models.CharField(max_length=256, db_index=True)
    warehouse = models.CharField(max_length=256, db_index=True)
    REPORTING = JSONField()
    WEB_BASED = JSONField()
    MULTIPLE_ORDERS = JSONField()
    OrderFormFreeOfGaps = JSONField()
    guidelineAdherenceAdult1L = JSONField()
    guidelineAdherenceAdult2L = JSONField()
    guidelineAdherencePaed1L = JSONField()
    nnrtiPaed = JSONField()
    nnrtiAdults = JSONField()
    stablePatientVolumes = JSONField()
    consumptionAndPatients = JSONField()
    warehouseFulfilment = JSONField()
    differentOrdersOverTime = JSONField()
    closingBalanceMatchesOpeningBalance = JSONField()
    orderFormFreeOfNegativeNumbers = JSONField()
    stableConsumption = JSONField()
    default_fail_count = models.IntegerField(default=0)
    default_pass_count = models.IntegerField(default=0)
    f1_fail_count = models.IntegerField(default=0)
    f1_pass_count = models.IntegerField(default=0)
    f2_fail_count = models.IntegerField(default=0)
    f2_pass_count = models.IntegerField(default=0)
    f3_fail_count = models.IntegerField(default=0)
    f3_pass_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ("name", "cycle", "district", "ip", "warehouse")


class Consumption(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    cycle = models.CharField(max_length=256, db_index=True)
    district = models.CharField(max_length=256, db_index=True)
    ip = models.CharField(max_length=256, db_index=True)
    warehouse = models.CharField(max_length=256, db_index=True)
    opening_balance = models.FloatField(null=True, blank=True)
    quantity_received = models.FloatField(null=True, blank=True)
    consumption = models.FloatField(null=True, blank=True)
    loses_adjustments = models.FloatField(null=True, blank=True)
    closing_balance = models.FloatField(null=True, blank=True)
    months_of_stock_on_hand = models.FloatField(null=True, blank=True)
    days_out_of_stock = models.FloatField(null=True, blank=True)
    quantity_required_for_current_patients = models.FloatField(null=True, blank=True)
    estimated_number_of_new_patients = models.FloatField(null=True, blank=True)
    estimated_number_of_new_pregnant_women = models.FloatField(null=True, blank=True)
    packs_ordered = models.FloatField(null=True, blank=True)
    notes = models.CharField(max_length=256, null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True, db_index=True)

    def __unicode__(self):
        return "%s %s" % (self.cycle, self.formulation)

    class Meta:
        verbose_name_plural = "Consumption Records"


class AdultPatientsRecord(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    cycle = models.CharField(max_length=256, db_index=True)
    district = models.CharField(max_length=256, db_index=True)
    ip = models.CharField(max_length=256, db_index=True)
    warehouse = models.CharField(max_length=256, db_index=True)
    existing = models.FloatField(null=True, blank=True)
    new = models.FloatField(null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.cycle, self.formulation)

    class Meta:
        verbose_name_plural = "Adult Patient Records"


class PAEDPatientsRecord(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    cycle = models.CharField(max_length=256, db_index=True)
    district = models.CharField(max_length=256, db_index=True)
    ip = models.CharField(max_length=256, db_index=True)
    warehouse = models.CharField(max_length=256, db_index=True)
    existing = models.FloatField(null=True, blank=True)
    new = models.FloatField(null=True, blank=True)
    formulation = models.CharField(max_length=256, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Paed Patient Records"

    def __unicode__(self):
        return "%s %s" % (self.cycle, self.formulation)


class MultipleOrderFacility(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    cycle = models.CharField(max_length=256, db_index=True)
    district = models.CharField(max_length=256, db_index=True)
    ip = models.CharField(max_length=256, db_index=True)
    warehouse = models.CharField(max_length=256, db_index=True)

    def __unicode__(self):
        return "%s %s" % (self.cycle, self.name)

    class Meta:
        verbose_name_plural = "Facilities with Multiple Orders"


class Dhis2StandardReport(models.Model):
    name = models.CharField(max_length=256, db_index=True, blank=False)
    report_id = models.CharField(max_length=256, db_index=True, blank=False)
    warehouse = models.CharField(choices=WAREHOUSES, max_length=50, blank=False)
    report_type = models.CharField(choices=REPORT_TYPES, max_length=50, blank=False)
    org_unit_id = models.CharField(max_length=20, db_index=True, blank=False)

    def __unicode__(self):
        return "%s" % self.name

    class Meta:
        verbose_name_plural = "DHIS2 Standard Reports"


class LocationToPartnerMapping(models.Model):
    mapping = PickledObjectField()

    def update(self, mapping):
        self.objects.all().delete()
        self.objects.create(mapping=mapping)

    @classmethod
    def get_mapping(cls):
        return FormattedKeyDict(cls.objects.first().mapping)


class FacilityTest(models.Model):
    name = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    last_updated = models.DateTimeField(auto_now=True, editable=False)
    definition = TestDefinitionField()
    description = models.TextField()
    short_description = models.TextField()

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name_plural = "Facility Tests"


class TracingFormulations(models.Model):
    name = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    formulations = JSONField()

    class Meta:
        verbose_name_plural = "Tracing Formulations"

    def __unicode__(self):
        return u'%s %s' % (self.name, self.model)