
import attr
from pydash import py_
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.data.user_defined import UserDefinedFacilityCheck
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
            model=DefinitionOption.from_dict(data.get('model')),
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


class GroupSerializer(serializers.Serializer):
    model = OptionField()
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


def build_field_filters(selected_fields):
    filter_kwargs = {}
    for field in selected_fields:
        filter_kwargs[field + "__isnull"] = False
    return filter_kwargs


def as_loc(items):
    if len(items) > 0:
        print(items, "-------")
        return {
            "name": items[0]['name'],
            "district": items[0]['district'],
            "cycles": [item['cycle'] for item in items]
        }
    else:
        return None


class DefinitionSerializer(serializers.Serializer):
    groups = serializers.ListField(child=GroupSerializer())
    type = serializers.DictField()

    def get_locations_and_cycles_with_data(self):
        definition = Definition.from_dict(self.validated_data)
        raw_locations = []
        for group in definition.groups:
            model = group.model.as_model()
            if model:
                field_filters = build_field_filters(group.selected_fields)
                base_queryset = model.objects.filter(formulation__in=group.selected_formulations, **field_filters)
                raw_locations.extend(
                    base_queryset.order_by('name').values(
                        'name', 'district', 'cycle').distinct())
        locations = py_(raw_locations).uniq().group_by('name').map(as_loc).sort_by("name").value()
        print(locations)
        return {"locations": locations}





testTypes = {
    "FacilityTwoGroups": UserDefinedFacilityCheck
}





class DefinitionSampleSerializer(DefinitionSerializer):
    sample = SampleSerializer()

    def get_preview_data(self):
        definition = Definition.from_dict(self.validated_data)
        testType = self.validated_data['type']['id']
        check = testTypes.get(testType)
        if check:
            return check(definition).get_preview_data()
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
