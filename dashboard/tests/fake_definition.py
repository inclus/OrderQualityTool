from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, Consumption


class FakeDefinition(object):
    class Builder(object):
        def __init__(self, data):
            self.data = data

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

        def on_group(self, f):
            group = self.data['groups'][0]
            f(group)
            return self

        def model(self, name):
            def f(group):
                group['model'] = {"id": ("%s" % name), "name": ("%s Records" % name)}

            return self.on_group(f)

        def get(self):
            return self.data

        def type(self, id):
            self.data["type"] = {"id": id}
            return self

        def factors(self, **factors):
            def f(group):
                if len(factors) > 0:
                    group['has_factors'] = True
                    group['factors'] = factors

            return self.on_group(f)

        def sample(self, location=None, cycle="cycle1"):
            if location is None:
                location = {"name": "loc1", "district": "dis1"}
            self.data["sample"] = {"location": location, "cycle": cycle}
            return self

        def tracing_formulations(self, *formulations):
            def f(group):
                group['model']['tracingFormulations'] = [{"formulations": formulations}]

            return self.on_group(f)

    def single(self):
        data = {
            "groups": [
                {
                    "name": "G1",
                    "cycle": {"id": "current", "name": "current"},
                }
            ]
        }
        return self.Builder(data).type("FacilityTwoGroups").aggregation("SUM").formulations("form_a", "form_b").fields(
            "new", "existing").model("Adult")

    def sampled(self, **kwargs):
        return self.single().sample(**kwargs)

    def traced(self, **kwargs):
        return self.single().type("FacilityTwoGroupsAndTracingFormulation").sample(
            **kwargs)


def gen_adult_record(name="loc1", district="dis1", formulation="form_a", cycle="cycle1", existing=12, new=1):
    AdultPatientsRecord.objects.create(
        name=name,
        district=district,
        formulation=formulation,
        existing=existing,
        new=new,
        cycle=cycle)


def gen_paed_record(name="loc1", district="dis1", formulation="form_a", cycle="cycle1", existing=20, new=10):
    PAEDPatientsRecord.objects.create(
        name=name,
        district=district,
        formulation=formulation,
        existing=existing,
        new=new,
        cycle=cycle)


def gen_consumption_record(name="loc1", district="dis1", formulation="form_a", cycle="cycle1", **fields):
    Consumption.objects.create(
        name=name,
        district=district,
        formulation=formulation,
        cycle=cycle, **fields)
