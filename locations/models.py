import json

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Location(MPTTModel):
    name = models.CharField(max_length=256, unique=False)
    uid = models.CharField(max_length=256, unique=True)
    org_level = models.CharField(max_length=50)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name


def get_or_create_location(uid, name, level, parent=None):
    try:
        location = Location.objects.get(uid=uid)
    except ObjectDoesNotExist:
        location = Location.objects.create(uid=uid, name=name, org_level=level, parent=parent)
    return location


def import_locations_from_json(json_text):
    units = json.loads(json_text)['organisationUnits']
    sorted_units = sorted(units, key=lambda x: x['level'])
    for unit in sorted_units:
        if 'parent' in unit:
            parent = get_or_create_location(unit['parent']['id'], unit['parent']['name'], unit['parent']['level'])
            get_or_create_location(unit['id'], unit['name'], unit['level'], parent)
        else:
            get_or_create_location(unit['id'], unit['name'], unit['level'])
