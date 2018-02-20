import json

import attr
from pydash import py_


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
        )

    @property
    def has_overrides(self):
        return len(py_(self.sample_formulation_model_overrides.values()).map(
            lambda x: dict(x).get("formulations", [])).flatten().value()) > 0


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
