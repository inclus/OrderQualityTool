import contextlib2

import responses
from pathlib2 import Path


@contextlib2.contextmanager
def fake_orgunit_response():
    json_fixture_path = Path(Path(__file__).resolve().parent, 'fixtures/units.json')
    with json_fixture_path.open() as json_fixture:
        base_url = 'http://localhost:8080'
        resource = 'api/organisationUnitGroupSets.json'
        filters = "name:eq:ARVs%20Warehouse"
        fields = "id,name,organisationUnitGroups[id,name,organisationUnits[id,name,ancestors[id,name,level]]]"
        # fields = 'ancestors[name,level],id,name'
        # filters = 'level:gte:5'
        responses.add(responses.GET,
                      '%s/%s?filter=%s&fields=%s' % (base_url, resource, filters, fields),
                      body=json_fixture.read(), status=200)
        yield
