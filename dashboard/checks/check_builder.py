from dashboard.checks.entities import Definition


class DefinitionFactory(object):
    class Builder(object):
        def __init__(self, data):
            self.data = data

        def add_group(self, position, aggegation, cycle, model, fields, formulations, factors=None):
            position_ = position + 1
            group = {
                "name": "G%d" % position_
                ,
                "cycle": {"id": cycle, "name": cycle},
                "aggregation": {"id": aggegation, "name": aggegation},
                "model": {"id": ("%s" % model), "name": ("%s Records" % model)},
                "selected_fields": fields,
                "selected_formulations": formulations,
            }
            if factors:
                group["hasFactors"] = True
                group["factors"] = factors

            self.data["groups"][position] = group
            return self

        def formulations(self, *formulations):
            def f(group):
                group['selected_formulations'] = formulations
                return group

            return self.on_group(f)

        def aggregation(self, id):
            def f(group):
                group['aggregation'] = {"id": id, "name": id}
                return group

            return self.on_group(f)

        def fields(self, *fields):
            def f(group):
                group['selected_fields'] = fields
                return group

            return self.on_group(f)

        def on_group(self, f):
            groups = self.data.get('groups', [])
            for index, group in enumerate(groups):
                if group:
                    self.data['groups'][index] = f(group)
            return self

        def model(self, name):
            def f(group):
                group['model'] = {"id": ("%s" % name), "name": ("%s Records" % name)}
                return group

            return self.on_group(f)

        def get(self):
            return self.data

        def getDef(self):
            return Definition.from_dict(self.data)

        def type(self, id):
            self.data["type"] = {"id": id}
            return self

        def factors(self, **factors):
            def f(group):
                if len(factors) > 0:
                    group['has_factors'] = True
                    group['factors'] = factors
                return group

            return self.on_group(f)

        def are_equal(self):
            self.data["operator"] = {"id": "AreEqual", "name": "AreEqual"}
            # self.data["operatorConstant"] = None
            return self

        def has_no_negatives(self):
            self.data["operator"] = {"id": "NoNegatives", "name": "NoNegatives"}
            # self.data["operatorConstant"] = None
            return self

        def is_less_than(self, ratio=1):
            self.data["operator"] = {"id": "LessThan", "name": "LessThan"}
            self.data["operatorConstant"] = ratio
            return self

        def sample(self, location=None, cycle="cycle1", tracer=None):
            if location is None:
                location = {"name": "loc1", "district": "dis1"}
            sample = {"location": location, "cycle": cycle}
            if tracer:
                sample['tracer'] = tracer
            self.data["sample"] = sample
            return self

        def tracing_formulations(self, *formulations):
            def f(group):
                group['model']['tracingFormulations'] = [{"formulations": formulations, "name": "trace1"}]
                return group

            return self.on_group(f)

        def python_class(self, class_name):
            self.data['python_class'] = class_name
            return self

        def at_least_of_total(self, ratio=80):
            self.data["operator"] = {"id": "AtLeastNOfTotal", "name": "LessThan"}
            self.data["operatorConstant"] = ratio
            return self

    def blank(self):
        return self.Builder({"groups": [{"fields": [], "formulations": [], "model": {}},
                                        {"fields": [], "formulations": [], "model": {}}]})

    def initial(self):
        group1 = {"name": "G1", "cycle": {"id": "current", "name": "current"}, }
        group2 = {"name": "G2", "cycle": {"id": "current", "name": "current"}, }
        data = {
            "groups": [
                group1,
                group2
            ]
        }
        return self.Builder(data).type("FacilityTwoGroups").aggregation("SUM").formulations("form_a", "form_b").fields(
            "new", "existing").model("Adult")

    def sampled(self, **kwargs):
        return self.initial().sample(**kwargs)

    def traced(self, **kwargs):
        return self.initial().type("FacilityTwoGroupsAndTracingFormulation").sample(
            **kwargs)

    def based_on_class(self, class_name):
        data = {
            "type": "ClassBased",
            "pythonClass": class_name
        }
        return self.Builder({}).type("ClassBased").python_class(class_name)


def class_based_check(class_name):
    return DefinitionFactory().based_on_class(class_name).get()


def guideline_adherence_adult1l_check():
    builder = DefinitionFactory().blank().type("FacilityTwoGroups")
    builder.add_group(0, "SUM", "current", "Consumption",
                      ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"],
                      ["Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]",
                       "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]"])
    builder.add_group(1, "SUM", "current", "Consumption",
                      ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"],
                      ["AZT/3TC/NVP 300/150/200mg", "AZT/3TC 300/150mg"])
    builder.at_least_of_total(80)

    return builder.get()


def guideline_adherence_adult2l_check():
    builder = DefinitionFactory().blank().type("FacilityTwoGroups")
    builder.add_group(0, "SUM", "current", "Consumption", ["estimated_number_of_new_patients"],
                      ["Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"])
    builder.add_group(1, "SUM", "current", "Consumption", ["estimated_number_of_new_patients"],
                      ["Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"])
    builder.is_less_than(73)

    return builder.get()


def guideline_paed1l_check():
    builder = DefinitionFactory().blank().type("FacilityTwoGroups")
    builder.add_group(0, "SUM", "current", "Consumption", ["estimated_number_of_new_patients"],
                      ["Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"])
    builder.add_group(1, "SUM", "current", "Consumption", ["estimated_number_of_new_patients"],
                      ["Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 60mg/30mg/50mg [Pack 60]",
                       "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"])
    builder.is_less_than(80)

    return builder.get()


def no_negatives_check():
    builder = DefinitionFactory().blank().type("FacilityTwoGroupsAndTracingFormulation")
    builder.add_group(0, "VALUES", "current", "Consumption",
                      ["opening_balance", "consumption", "closing_balance", "estimated_number_of_new_patients"],
                      [])
    builder.has_no_negatives()
    return builder.get()


def no_blanks_check():
    builder = DefinitionFactory().blank().type("FacilityTwoGroupsAndTracingFormulation")
    builder.add_group(0, "VALUES", "current", "Consumption",
                      ["opening_balance", "consumption", "closing_balance", "estimated_number_of_new_patients"],
                      [])
    builder.has_no_negatives()
    return builder.get()


def volume_tally_check():
    builder = DefinitionFactory().blank().type("FacilityTwoGroupsAndTracingFormulation")
    builder.add_group(0, "SUM", "current", "Consumption", ["consumption"], [],
                      factors={
                          "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]": 0.5,
                          "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]": 1 / 4.6,
                          "Efavirenz (EFV) 200mg [Pack 90]": 1,
                      })
    builder.add_group(1, "VALUES", "previous", "Paed", ["new", "existing"], [])
    builder.is_less_than(30)
    return builder.get()


def non_repeating_check():
    return no_blanks_check()


def open_closing_check():
    return no_blanks_check()


def stable_consumption_check():
    return no_blanks_check()


def nnrti_paed():
    return no_blanks_check()


def warehouse_fulfillment_check():
    return no_blanks_check()


def nnrti_adult():
    return no_blanks_check()
