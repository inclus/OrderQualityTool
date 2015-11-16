import os

from django.core.management import BaseCommand

from locations.models import import_locations_from_json


class Command(BaseCommand):
    def handle(self, *args, **options):
        fixture_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'json', 'units.json')
        with open(fixture_path, 'rb') as file_handle:
            json_text = file_handle.read()
            import_locations_from_json(json_text)
