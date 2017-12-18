import attr
from pydash import py_
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.data.user_defined import UserDefinedFacilityCheck, UserDefinedFacilityTracedCheck
from dashboard.models import AdultPatientsRecord, PAEDPatientsRecord, Consumption, TracingFormulations


@attr.s(cmp=True, frozen=True)
class DefinitionOption(object):
    id = attr.ib()
    name = attr.ib()

    @staticmethod
    def from_dict(data):
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

    def as_model(self):
        models = {'Adult': AdultPatientsRecord, 'Paed': PAEDPatientsRecord, 'Consumption': Consumption}
        if self.id in models:
            return models.get(self.id)
        else:
            return None


@attr.s(cmp=True, frozen=True)
class DefinitionGroup(object):
    name = attr.ib()
    model = attr.ib()
    cycle = attr.ib()
    selected_fields = attr.ib()
    selected_formulations = attr.ib()
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
            has_factors=data.get('has_factors'),
            factors=data.get('factors'),
        )


@attr.s(cmp=True, frozen=True)
class Definition(object):
    groups = attr.ib()
    type = attr.ib()
    sample = attr.ib()

    @staticmethod
    def from_dict(data):
        return Definition(
            groups=map(DefinitionGroup.from_dict, data.get('groups', [])),
            type=data.get('type'),
            sample=data.get('sample')
        )


class OptionField(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()


class GroupModelField(OptionField):
    tracingFormulations = serializers.ListField(child=serializers.DictField(), required=False)


class GroupSerializer(serializers.Serializer):
    model = GroupModelField()
    cycle = OptionField()
    name = serializers.CharField()
    selected_fields = serializers.ListField(child=serializers.CharField())
    selected_formulations = serializers.ListField(child=serializers.CharField())
    aggregation = OptionField()
    has_factors = serializers.BooleanField(required=False)
    factors = serializers.DictField(required=False)


class SampleSerializer(serializers.Serializer):
    location = serializers.DictField()
    cycle = serializers.CharField(required=False)
    tracer = serializers.DictField(required=False)


class DefinitionSerializer(serializers.Serializer):
    groups = serializers.ListField(child=GroupSerializer())
    type = serializers.DictField()

    def get_check(self):
        definition = Definition.from_dict(self.validated_data)
        testType = self.validated_data['type']['id']
        check_class = testTypes.get(testType)
        if check_class:
            return check_class(definition)
        return None

    def get_locations_and_cycles_with_data(self):
        check = self.get_check()
        if check:
            return check.get_locations_and_cycles()
        return {}


testTypes = {
    "FacilityTwoGroups": UserDefinedFacilityCheck,
    "FacilityTwoGroupsAndTracingFormulation": UserDefinedFacilityTracedCheck,
}


class DefinitionSampleSerializer(DefinitionSerializer):
    sample = SampleSerializer()

    def get_preview_data(self):
        check = self.get_check()
        if check:
            return check.get_preview_data()
        return {}


class PreviewDefinitionView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = DefinitionSampleSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.get_preview_data())
        else:
            return Response(data=serializer.errors, status=400)


class PreviewLocationsView(APIView):
    authentication_classes = []

    def post(self, request):
        serializer = DefinitionSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.get_locations_and_cycles_with_data())
        else:
            return Response(data=serializer.errors, status=400)


class ConsumptionTracingFormulationView(APIView):
    model = "Consumption"

    def get(self, request):
        tracers = [{"name": tracer.name, "formulations": tracer.formulations} for tracer in
                   TracingFormulations.objects.filter(model=self.model)]
        return Response(data=tracers)


class PatientTracingFormulationView(ConsumptionTracingFormulationView):
    model = "Patients"
