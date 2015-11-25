from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=256, unique=False)
    uid = models.CharField(max_length=256, unique=True)
    level = models.CharField(max_length=50)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __unicode__(self):
        return self.name
