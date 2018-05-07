import json

import attr
import pydash
from pydash import py_
from pymaybe import maybe

from dashboard.checks.tracer import Tracer
from dashboard.checks.utils import as_float_or_1, as_number


@attr.s(cmp=True, frozen=True)
class DefinitionOption(object):
    id = attr.ib()
    name = attr.ib()

    @staticmethod
    def from_dict(data):
        if data:
            return DefinitionOption(
                id=data.get('id', ''),
                name=data.get('name', ''),
            )


@attr.s(cmp=True, frozen=True)
class GroupModel(DefinitionOption):
    tracing_formulations = attr.ib()
    has_trace = attr.ib()

    @staticmethod
    def from_dict(data):
        return GroupModel(
            id=data.get('id', ''),
            name=data.get('name', ''),
            tracing_formulations=data.get('tracingFormulations', []),
            has_trace=data.get('hasTrace', False),
        )

    def get_records(self, location_data, id=None):
        models = {'Adult': "a_records", 'Paed': "p_records", 'Consumption': "c_records"}
        if id is None:
            id = self.id
        if id in models:
            return getattr(location_data, models.get(id))
        else:
            return []

    def as_model(self, model_id=None):
        from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, Consumption
        models = {'Adult': AdultPatientsRecord, 'Paed': PAEDPatientsRecord, 'Consumption': Consumption}
        if model_id is None:
            model_id = self.id
        if model_id in models:
            return models.get(model_id)
        else:
            return None


@attr.s(cmp=True, frozen=True)
class DefinitionGroup(object):
    name = attr.ib()
    model = attr.ib()
    cycle = attr.ib()
    selected_fields = attr.ib()
    selected_formulations = attr.ib()
    sample_formulation_model_overridden = attr.ib()
    sample_formulation_model_overrides = attr.ib()
    aggregation = attr.ib()
    has_factors = attr.ib()
    factors = attr.ib()
    has_thresholds = attr.ib()
    thresholds = attr.ib()

    @staticmethod
    def from_dict(data):
        return DefinitionGroup(
            model=GroupModel.from_dict(data.get('model')),
            name=data.get('name'),
            cycle=DefinitionOption.from_dict(data.get('cycle')),
            aggregation=DefinitionOption.from_dict(data.get('aggregation')),
            selected_fields=data.get('selected_fields'),
            selected_formulations=data.get('selected_formulations'),
            sample_formulation_model_overrides=data.get('sample_formulation_model_overrides', {}),
            sample_formulation_model_overridden=data.get('sample_formulation_model_overridden', {}),
            has_factors=data.get('has_factors'),
            factors=data.get('factors'),
            has_thresholds=data.get('has_thresholds'),
            thresholds=data.get('thresholds'),
        )

    @property
    def has_overrides(self):
        return len(py_(self.sample_formulation_model_overrides.values()).map(
            lambda x: dict(x).get("formulations", [])).flatten().value()) > 0

    def get_formulations(self, tracer):
        models = {'Adult': "patient_formulations", 'Paed': "patient_formulations",
                  'Consumption': "consumption_formulations"}
        key = models.get(self.model.id)
        if tracer is not None and type(tracer) is Tracer:
            if tracer.key == "DEFAULT":
                return self.selected_formulations

            return py_(self.model.tracing_formulations).find(
                {"slug": tracer.key}).value().get(key)
        else:
            return self.selected_formulations


@attr.s(cmp=True, frozen=True)
class Definition(object):
    groups = attr.ib()
    type = attr.ib()
    sample = attr.ib()
    operator = attr.ib()
    python_class = attr.ib()
    operator_constant = attr.ib()

    @staticmethod
    def from_dict(data):
        return Definition(
            groups=py_(data.get('groups', [])).map(DefinitionGroup.from_dict).value(),
            type=data.get('type'),
            python_class=data.get('python_class'),
            sample=data.get('sample'),
            operator=DefinitionOption.from_dict(data.get('operator')),
            operator_constant=data.get('operatorConstant'),
        )

    @staticmethod
    def from_string(definition):
        try:
            return Definition.from_dict(json.loads(definition))
        except ValueError as e:
            return Definition.from_dict({})


@attr.s(cmp=True, frozen=True)
class GroupResult(object):
    group = attr.ib()
    values = attr.ib()
    factored_records = attr.ib()
    aggregate = attr.ib()
    tracer = attr.ib()

    def is_above_threshold(self):
        if self.has_thresholds():
            threshold = self.get_threshold()
            aggregate = self.aggregate
            print(aggregate, threshold)
            return aggregate >= threshold
        else:
            return True

    def has_thresholds(self):
        return self.group.has_thresholds and maybe(self.group.thresholds).or_else({}).get(self.tracer.key, None)

    def get_threshold(self):
        raw_value = self.group.thresholds.get(self.tracer.key, None)
        return as_float_or_1(raw_value, 0) if raw_value else raw_value

    def all_values_blank(self):
        return pydash.every(self.factored_records, lambda data_record: data_record.all_blank())

    def some_values_blank(self):
        return pydash.some(self.factored_records, lambda data_record: data_record.some_blank())

    def as_dict(self):
        return {
            "name": self.group.name,
            "aggregation": self.group.aggregation.name,
            "values": [v.to_list() for v in self.values],
            "headers": self.group.selected_fields,
            "has_factors": self.group.has_factors,
            "factored_values": [v.to_list() for v in self.factored_records],
            "result": self.aggregate
        }


@attr.s(cmp=True, frozen=True)
class DataRecord(object):
    formulation = attr.ib()
    values = attr.ib()
    fields = attr.ib()

    def to_list(self):
        values = [self.formulation]
        values.extend(self.values)
        return values

    def all_blank(self):
        return pydash.every(self.values, lambda x: x is None)

    def some_blank(self):
        return pydash.some(self.values, lambda x: x is None)

    @staticmethod
    def from_list(data, fields=[]):
        return DataRecord(formulation=data[0], values=data[1:], fields=fields)

    def factor(self, factors=None):
        if factors is None:
            factors = {}

        factor = as_float_or_1(factors.get(self.formulation, 1))
        new_values = []
        for value in self.values:
            is_numerical, numerical_value = as_number(value)
            if is_numerical:
                new_values.append(numerical_value * factor)
            else:
                new_values.append(value)
        return attr.evolve(self, values=new_values)
