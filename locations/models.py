from django.db import models
from django.db.models import Model, ForeignKey


class Location(Model):
    name = models.CharField(max_length=256, unique=False)
    uid = models.CharField(max_length=256, unique=True)
    level = models.CharField(max_length=50)
    parent = ForeignKey('self', null=True, blank=True, related_name='children')

    def __unicode__(self):
        return self.name
