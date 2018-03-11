from dashboard.checks.entities import Definition

OPERATOR = "operator"

SUM = "SUM"

VALUE = "VALUE"

F3_PATIENT_QUERY = ["ABC/3TC/EFV", "AZT/3TC/EFV"]

F2_PATIENT_QUERY = ["ABC/3TC/LPV/r", "ABC/3TC/EFV", "ABC/3TC/NVP"]
F3 = "EFV200 (Paed)"
F2 = "ABC/3TC (Paed)"
F1 = "TDF/3TC/EFV (Adult)"
F1_PATIENT_QUERY = ["TDF/3TC/EFV (PMTCT)", "TDF/3TC/EFV (ADULT)"]
F1_QUERY = ["Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]"]
F3_QUERY = ["Efavirenz (EFV) 200mg [Pack 90]"]
F2_QUERY = ["Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"]
CONSUMPTION_MODEL = "Consumption"
FORMULATIONS = "formulations"
TRACING_FORMULATIONS = "tracingFormulations"
NAME = "name"
FACILITY_TWO_GROUPS = "FacilityTwoGroups"
CURRENT_CYCLE = "Current"
PREVIOUS_CYCLE = "Previous"
FACILITY_TWO_GROUPS_WITH_SAMPLE = "FacilityTwoGroupsAndTracingFormulation"


def build_model(name, check_type):
    model = {"id": ("%s" % name), NAME: ("%s Records" % name)}
    if check_type and check_type["id"] == FACILITY_TWO_GROUPS_WITH_SAMPLE:
        model["hasTrace"] = True
        if name.lower() in ["paed", "adult"]:
            model[TRACING_FORMULATIONS] = [
                {NAME: F1, FORMULATIONS: F1_PATIENT_QUERY},
                {NAME: F2, FORMULATIONS: F2_PATIENT_QUERY},
                {NAME: F3, FORMULATIONS: F3_PATIENT_QUERY}, ]
        if name.lower() in [CONSUMPTION_MODEL.lower()]:
            model[TRACING_FORMULATIONS] = [
                {NAME: F1, FORMULATIONS: F1_QUERY},
                {NAME: F2, FORMULATIONS: F2_QUERY},
                {NAME: F3, FORMULATIONS: F3_QUERY}, ]
    return model


def override_models_on_group(group, overrides):
    for (key, value) in overrides.items():
        if 'sample_formulation_model_overridden' not in group:
            group['sample_formulation_model_overridden'] = {}
            group['sample_formulation_model_overrides'] = {}
        group['sample_formulation_model_overridden'][key] = True
        group['sample_formulation_model_overrides'][key] = value


class DefinitionFactory(object):
    class Builder(object):
        def __init__(self, data):
            self.data = data

        def add_group(self, name, aggregation, cycle, model, fields, formulations, factors=None, model_overrides=None):
            id = "id"
            group = {
                NAME: name,
                "cycle": {id: cycle, NAME: "%s Cycle" % cycle},
                "aggregation": {"id": aggregation, NAME: aggregation},
                "model": build_model(model, self.data["type"]),
                "selected_fields": fields,
                "selected_formulations": formulations,
            }
            if factors:
                group["has_factors"] = True
                group["factors"] = factors

            if model_overrides is not None:
                override_models_on_group(group, model_overrides)

            self.data["groups"].append(group)
            return self

        def formulations(self, *formulations):
            def f(group):
                group['selected_formulations'] = formulations
                return group

            return self.on_group(f)

        def aggregation(self, id):
            def f(group):
                group['aggregation'] = {"id": id, NAME: id}
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
                model = build_model(name, self.data["type"])

                group['model'] = model
                return group

            return self.on_group(f)

        def model_overrides(self, overrides):
            def f(group):
                override_models_on_group(group, overrides)
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
            self.data["operator"] = {"id": "AreEqual", NAME: "AreEqual"}
            return self

        def are_not_equal(self):
            self.data["operator"] = {"id": "AreNotEqual", NAME: "AreNotEqual"}
            return self

        def has_no_negatives(self):
            self.data["operator"] = {"id": "NoNegatives", NAME: "NoNegatives"}
            return self

        def percentage_variance_is_less_than(self, ratio=1):
            self.data[OPERATOR] = {"id": "LessThan", NAME: "Percentage Variance is less than"}
            self.data["operatorConstant"] = ratio
            return self

        def sample(self, location=None, cycle="cycle1", tracer=None):
            if location is None:
                location = {NAME: "loc1", "district": "dis1"}
            sample = {"location": location, "cycle": cycle}
            if tracer:
                sample['tracer'] = tracer
            self.data["sample"] = sample
            return self

        def tracing_formulations(self, *formulations):
            def f(group):
                group['model']['tracingFormulations'] = [{FORMULATIONS: formulations, NAME: "trace1"}]
                return group

            return self.on_group(f)

        def python_class(self, class_name):
            self.data['python_class'] = class_name
            return self

        def at_least_of_total(self, ratio=100):
            self.data["operator"] = {"id": "AtLeastNOfTotal", NAME: "LessThan"}
            self.data["operatorConstant"] = ratio
            return self

        def has_no_blanks(self):
            self.data["operator"] = {"id": "NoBlanks", NAME: "NoBlanks"}
            return self

    def blank(self):
        return self.Builder({"groups": []})

    def initial(self):
        group1 = {NAME: "G1", "cycle": {"id": CURRENT_CYCLE, NAME: CURRENT_CYCLE}, }
        group2 = {NAME: "G2", "cycle": {"id": CURRENT_CYCLE, NAME: CURRENT_CYCLE}, }
        data = {
            "groups": [
                group1,
                group2
            ]
        }
        return self.Builder(data).type(FACILITY_TWO_GROUPS).aggregation("SUM").formulations("form_a", "form_b").fields(
            "new", "existing").model("Adult")

    def sampled(self, **kwargs):
        return self.initial().sample(**kwargs).are_equal()

    def traced(self, **kwargs):
        return self.initial().type(FACILITY_TWO_GROUPS_WITH_SAMPLE).sample(
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
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"],
                      ["Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]",
                       "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]"])
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["estimated_number_of_new_patients", "estimated_number_of_new_pregnant_women"],
                      ["AZT/3TC/NVP 300/150/200mg", "AZT/3TC 300/150mg"])
    builder.at_least_of_total(80)

    return builder.get()


def guideline_adherence_adult2l_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["estimated_number_of_new_patients"],
                      ["Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]"])
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["estimated_number_of_new_patients"],
                      ["Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]"])
    builder.at_least_of_total(73)

    return builder.get()


def guideline_paed1l_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["estimated_number_of_new_patients"],
                      ["Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]"])
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["estimated_number_of_new_patients"],
                      ["Zidovudine/Lamivudine/Nevirapine (AZT/3TC/NVP) 60mg/30mg/50mg [Pack 60]",
                       "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"])
    builder.at_least_of_total(80)

    return builder.get()


def no_negatives_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["opening_balance", "consumption", "closing_balance", "estimated_number_of_new_patients"],
                      [])
    builder.has_no_negatives()
    return builder.get()


def no_blanks_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["opening_balance", "consumption", "closing_balance", "estimated_number_of_new_patients"],
                      [])
    builder.has_no_blanks()
    return builder.get()


def volume_tally_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [],
                      factors={
                          "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]": 0.5,
                          "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]": 1 / 4.6,
                          "Efavirenz (EFV) 200mg [Pack 90]": 1,
                      })
    builder.add_group("G2", SUM, CURRENT_CYCLE, "Adult", ["new", "existing"], [],
                      model_overrides={F2: {"id": "Paed", "formulations": F2_PATIENT_QUERY},
                       F3: {"id": "Paed", "formulations": F3_PATIENT_QUERY}})
    builder.percentage_variance_is_less_than(30)
    return builder.get()


def non_repeating_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    formulations = ["consumption", "opening_balance", "days_out_of_stock"]
    builder.add_group("G0", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL, formulations, [])
    builder.add_group("G1", VALUE, PREVIOUS_CYCLE, CONSUMPTION_MODEL, formulations, [])
    builder.are_not_equal()
    return builder.get()


def open_closing_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["opening_balance"], [])
    builder.add_group("G2", VALUE, PREVIOUS_CYCLE, CONSUMPTION_MODEL,
                      ["closing_balance"], [])
    builder.are_equal()
    return builder.get()


def stable_consumption_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [])
    builder.add_group("G2", SUM, PREVIOUS_CYCLE, CONSUMPTION_MODEL, ["consumption"], [])
    builder.percentage_variance_is_less_than(50)
    return builder.get()


def warehouse_fulfillment_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL, ["quantity_received"], [])
    builder.add_group("G2", VALUE, PREVIOUS_CYCLE, CONSUMPTION_MODEL, ["packs_ordered"], [])
    builder.are_equal()
    return builder.get()


def nnrti_paed():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]",
        "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]",
        "Efavirenz (EFV) 200mg [Pack 90]"
    ], factors={
        "Efavirenz (EFV) 200mg [Pack 90]": 1,
        "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]": 4.6,
        "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]": 4.6,
    })
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Nevirapine (NVP) 50mg [Pack 60]",
        "Lopinavir/Ritonavir (LPV/r) 80mg/20ml oral susp [Bottle 60ml]",
        "Lopinavir/Ritonavir (LPV/r) 100mg/25mg",
    ])
    builder.percentage_variance_is_less_than(30)
    return builder.get()


def nnrti_adult():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]",
        "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]",
        "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]"
    ], factors={
        "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]": 2,
        "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]": 2,
        "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]": 2,
    })
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Efavirenz (EFV) 600mg [Pack 30]",
        "Nevirapine (NVP) 200mg [Pack 60]",
        "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]",
        "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]",
        "Dolutegravir (DTG) 50mg"
    ])
    builder.percentage_variance_is_less_than(30)
    return builder.get()
