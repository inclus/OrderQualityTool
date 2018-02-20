import contextlib2

import responses
from pathlib2 import Path


@contextlib2.contextmanager
def fake_orgunit_response():
    json_fixture_path = Path(Path(__file__).resolve().parent, 'fixtures/units.json')
    with json_fixture_path.open() as json_fixture:
        base_url = 'http://localhost:8080'
        resource = 'api/organisationUnits.json'
        fields = 'ancestors[name,level],id,name'
        filters = 'level:gte:5'
        responses.add(responses.GET,
                      '%s/%s?fields=%s&filter=%s&paging=false' % (base_url, resource, fields, filters),
                      body=json_fixture.read(), status=200)
        yield