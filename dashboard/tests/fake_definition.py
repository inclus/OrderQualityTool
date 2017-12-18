from dashboard.models import AdultPatientsRecord


class FakeDefinition(object):

    def __init__(self):
        self.data = {}

    def single(self):
        self.data = {
            "type": {"id": "FacilityTwoGroups"},
            "groups": [
                {
                    "name": "G1",
                    "cycle": {"id": "current", "name": "current"},
                }
            ]
        }
        return self.aggregation("SUM").formulations("form_a", "form_b").fields("new", "existing").model("Adult")

    def formulations(self, *formulations):
        def f(group):
            group['selected_formulations'] = formulations

        return self.on_group(f)

    def aggregation(self, id):
        def f(group):
            group['aggregation'] = {"id": id, "name": id}

        return self.on_group(f)

    def fields(self, *fields):
        def f(group):
            group['selected_fields'] = fields

        return self.on_group(f)

    def get(self):
        return self.data

    def on_group(self, f):
        group = self.data['groups'][0]
        f(group)
        return self

    def model(self, name):
        def f(group):
            group['model'] = {"id": ("%s" % name), "name": ("%s Records" % name)}

        return self.on_group(f)


def gen_adult_record(name="loc1", district="dis1", formulation="form_a", cycle="cycle1", existing=12, new=1):
    AdultPatientsRecord.objects.create(
        name=name,
        district=district,
        formulation=formulation,
        existing=existing,
        new=new,
        cycle=cycle)