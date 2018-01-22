from rest_framework import serializers

from dashboard.checks.entities import Definition
from dashboard.checks.user_defined_check import get_check


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
    operator = OptionField(required=False)
    operatorConstant = serializers.CharField(required=False)
    python_class = serializers.CharField(required=False)

    def get_locations_and_cycles_with_data(self):
        definition = self.get_definition()
        check = get_check(definition)
        if check:
            return check.get_locations_and_cycles()
        return {}

    def get_definition(self):
        definition = Definition.from_dict(self.validated_data)
        return definition


class DefinitionSampleSerializer(DefinitionSerializer):
    sample = SampleSerializer()

    def get_preview_data(self):
        definition = self.get_definition()
        check = get_check(definition)
        if check:
            return check.get_preview_data()
        return {}
