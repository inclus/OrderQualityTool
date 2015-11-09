import json
import os

from django.core.management import BaseCommand

from locations.models import Location


class Command(BaseCommand):
    def handle(self, *args, **options):
        fixture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json', 'units.json')
        with open(fixture_path, 'rb') as file_handle:
            json_text = file_handle.read()
            units = json.loads(json_text)['organisationUnits']
            for unit in units:
                if 'parent' in unit:
                    parent, created = Location.objects.get_or_create(name=unit['parent']['name'], uid=unit['parent']['id'], level=unit['parent']['level'])
                    loc, created = Location.objects.get_or_create(name=unit['name'], uid=unit['id'], level=unit['level'])
                    loc.parent = parent
                    loc.save()
                else:
                    Location.objects.get_or_create(name=unit['name'], uid=unit['id'], level=unit['level'])
