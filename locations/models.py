from django.db import models


class WareHouse(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class IP(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __unicode__(self):
        return self.name


class Facility(models.Model):
    name = models.CharField(max_length=256, unique=True)
    warehouse = models.ForeignKey(WareHouse, null=True, blank=True, related_name="facilities")
    ip = models.ForeignKey(IP, null=True, blank=True, related_name="facilities")
    district = models.ForeignKey(District, null=True, blank=True, related_name="facilities")

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "facilities"
