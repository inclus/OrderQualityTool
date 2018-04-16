from dashboard.checks.entities import Definition
from dashboard.checks.tracer import Tracer
from dashboard.models import TracingFormulations

ADULT_MODEL = "Adult"
PAED_MODEL = "Paed"

OPERATOR = "operator"

SUM = "SUM"

VALUE = "VALUE"

CONSUMPTION_MODEL = "Consumption"
FORMULATIONS = "formulations"
NAME = "name"
FACILITY_TWO_GROUPS = "FacilityTwoGroups"
FACILITY_ONE_GROUP = "FacilityOneGroup"
CURRENT_CYCLE = "Current"
PREVIOUS_CYCLE = "Previous"
FACILITY_TWO_GROUPS_WITH_SAMPLE = "FacilityTwoGroupsAndTracingFormulation"


def build_model(name, check_type):
    model = {"id": ("%s" % name), NAME: ("%s Records" % name)}
    if check_type and check_type["id"] == FACILITY_TWO_GROUPS_WITH_SAMPLE:
        model["hasTrace"] = True
        model["tracingFormulations"] = [tracing_formulation.as_dict_obj() for tracing_formulation in
                                        TracingFormulations.objects.all()]
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

        def add_group(self, name, aggregation, cycle, model, fields, formulations, factors=None, model_overrides=None,
                      thresholds=None):
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

            if thresholds:
                group["has_thresholds"] = True
                group["thresholds"] = thresholds

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

        def type(self, id, name=None):
            self.data["type"] = {"id": id}
            if name is not None:
                self.data["type"]["name"] = name
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
            self.data[OPERATOR] = {"id": "LessThan", NAME: "Percentage Variance is less than N%"}
            self.data["operatorConstant"] = ratio
            return self

        def nnrti_percentage_variance_is_less_than(self, ratio=1):
            self.data[OPERATOR] = {"id": "NNRTILessThan", NAME: "FOR NNRTI Percentage Variance is less than N%"}
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

        def tracing_formulations(self, key, *formulations):
            def f(group):
                patient_formulations = 'patient_formulations'
                group['model']['tracingFormulations'] = [
                    {key: formulations, NAME: "trace1", "slug": "trace1"}]
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
        return self.Builder({}).type("ClassBased", "Class Based Facility Check").python_class(class_name)


def class_based_check(class_name):
    return DefinitionFactory().based_on_class(class_name).get()


def guideline_adherence_adult1l_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, ADULT_MODEL,
                      ["new"],
                      ["TDF/3TC/EFV (PMTCT)", "TDF/3TC/EFV (ADULT)"])
    builder.add_group("G2", SUM, CURRENT_CYCLE, ADULT_MODEL,
                      ["new"],
                      ["ABC/3TC/AZT (ADULT)", "ABC/3TC/AZT (PMTCT)", 'ABC/3TC/EFV (ADULT)', 'ABC/3TC/EFV (PMTCT)',
                       'ABC/3TC/NVP (ADULT)', 'ABC/3TC/NVP (PMTCT)', 'AZT/3TC/EFV (ADULT)', 'AZT/3TC/EFV (PMTCT)',
                       'AZT/3TC/NVP (ADULT)', 'AZT/3TC/NVP (PMTCT)', 'TDF/3TC/AZT (ADULT)', 'TDF/3TC/AZT (PMTCT)'])
    builder.at_least_of_total(90)

    return builder.get()


def guideline_adherence_adult2l_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, ADULT_MODEL, ["new"],
                      ["ABC/3TC/ATV/r (ADULT)", "ABC/3TC/ATV/r (PMTCT)", "AZT/3TC/ATV/r (ADULT)",
                       "AZT/3TC/ATV/r (PMTCT)", "TDF/3TC/ATV/r (ADULT)", "TDF/3TC/ATV/r (PMTCT)"])
    builder.add_group("G2", SUM, CURRENT_CYCLE, ADULT_MODEL, ["new"],
                      ["ABC/3TC/LPV/r (ADULT)", "ABC/3TC/LPV/r (PMTCT)", "AZT/3TC/LPV/r (ADULT)",
                       "AZT/3TC/LPV/r (PMTCT)", "TDF/3TC/LPV/r (ADULT)", "TDF/3TC/LPV/r (PMTCT)"])
    builder.at_least_of_total(80)

    return builder.get()


def guideline_paed1l_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, PAED_MODEL, ["new"],
                      ["ABC/3TC/EFV", "ABC/3TC/NVP", "ABC/3TC/LPV/r"])
    builder.add_group("G2", SUM, CURRENT_CYCLE, PAED_MODEL, ["new"],
                      ["AZT/3TC/ABC",
                       "AZT/3TC/EFV", "AZT/3TC/LPV/r", "AZT/3TC/NVP"])
    builder.at_least_of_total(80)

    return builder.get()


def no_negatives_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["opening_balance", "consumption", "closing_balance", "estimated_number_of_new_patients",
                       "quantity_received"],
                      [])
    builder.has_no_negatives()
    return builder.get()


def no_blanks_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL,
                      ["opening_balance", "closing_balance", "loses_adjustments", "quantity_received", "consumption"],
                      [])
    builder.has_no_blanks()
    return builder.get()


def volume_tally_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("Patients in Current Cycle", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [],
                      factors={
                          "Tenofovir/Lamivudine/Efavirenz (TDF/3TC/EFV) 300mg/300mg/600mg[Pack 30]": 0.5,
                          "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]": 1 / 4.6,
                          "Efavirenz (EFV) 200mg [Pack 90]": 1,
                      })
    f2 = Tracer.F2()
    f3 = Tracer.F3()
    builder.add_group("G2", SUM, CURRENT_CYCLE, "Adult", ["new", "existing"], [],
                      model_overrides={
                          f2.key: {"id": "Paed", "formulations": f2.patient_formulations},
                          f3.key: {"id": "Paed", "formulations": f3.patient_formulations}
                      })
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
    thresholds = {Tracer.F1().key: 20, Tracer.F2().key: 10, Tracer.F3().key: 10}
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [], thresholds=thresholds)
    builder.add_group("G2", SUM, PREVIOUS_CYCLE, CONSUMPTION_MODEL, ["consumption"], [], thresholds=thresholds)
    builder.percentage_variance_is_less_than(50)
    return builder.get()


def stable_patients_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    f2 = Tracer.F2()
    f3 = Tracer.F3()
    thresholds = {Tracer.F1().key: "20", f2.key: "10", f3.key: "10"}
    model_overrides = {f2.key: {"id": "Paed", "formulations": f2.patient_formulations},
                       f3.key: {"id": "Paed", "formulations": f3.patient_formulations}}
    builder.add_group("G1", SUM, CURRENT_CYCLE, ADULT_MODEL, ["existing", "new"], [], thresholds=thresholds,
                      model_overrides=model_overrides)
    builder.add_group("G2", SUM, PREVIOUS_CYCLE, ADULT_MODEL, ["existing", "new"], [], thresholds=thresholds,
                      model_overrides=model_overrides)
    builder.percentage_variance_is_less_than(50)
    return builder.get()


def warehouse_fulfillment_check():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS_WITH_SAMPLE)
    builder.add_group("G1", VALUE, CURRENT_CYCLE, CONSUMPTION_MODEL, ["quantity_received"], [])
    builder.add_group("G2", VALUE, PREVIOUS_CYCLE, CONSUMPTION_MODEL, ["packs_ordered"], [])
    builder.are_equal()
    return builder.get()


def nnrti_paed():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]",
        "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]"
    ], factors={
        "Zidovudine/Lamivudine (AZT/3TC) 60mg/30mg [Pack 60]": "0.25",
        "Abacavir/Lamivudine (ABC/3TC) 60mg/30mg [Pack 60]": "0.5",
    })
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Efavirenz (EFV) 200mg [Pack 90]",
        "Lopinavir/Ritonavir (LPV/r) 100mg/25mg",
        "Nevirapine (NVP) 50mg [Pack 60]",
        "Lopinavir/Ritonavir (LPV/r) 40mg/10mg Pellets [Pack of 120]",
    ], factors={'Efavirenz (EFV) 200mg [Pack 90]': '0.5',
                'Lopinavir/Ritonavir (LPV/r) 100mg/25mg': '0.5',
                'Lopinavir/Ritonavir (LPV/r) 40mg/10mg Pellets [Pack of 120]': '0.25',
                'Nevirapine (NVP) 50mg [Pack 60]': '0.5',
                'consumption': 1})
    builder.nnrti_percentage_variance_is_less_than(30)
    return builder.get()


def nnrti_adult():
    builder = DefinitionFactory().blank().type(FACILITY_TWO_GROUPS)
    builder.add_group("G1", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]",
        "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]",
        "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]",
    ], factors={
        "Zidovudine/Lamivudine (AZT/3TC) 300mg/150mg [Pack 60]": '0.5',
        "Tenofovir/Lamivudine (TDF/3TC) 300mg/300mg [Pack 30]": '0.5',
        "Abacavir/Lamivudine (ABC/3TC) 600mg/300mg [Pack 30]": '0.5',
    })
    builder.add_group("G2", SUM, CURRENT_CYCLE, CONSUMPTION_MODEL, ["consumption"], [
        "Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]",
        "Efavirenz (EFV) 600mg [Pack 30]",
        "Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]",
        "Nevirapine (NVP) 200mg [Pack 60]",
    ], factors={'Atazanavir/Ritonavir (ATV/r) 300mg/100mg [Pack 30]': '0.5',
                'Efavirenz (EFV) 600mg [Pack 30]': '0.5',
                'Lopinavir/Ritonavir (LPV/r) 200mg/50mg [Pack 120]': '0.5',
                'Nevirapine (NVP) 200mg [Pack 60]': '0.5',
                'consumption': 1})
    builder.nnrti_percentage_variance_is_less_than(30)
    return builder.get()
