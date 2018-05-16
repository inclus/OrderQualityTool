from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from dashboard.models import Score


class FacilityScoreSerializer(ModelSerializer):

    class Meta:
        model = Score


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class ScoreSerializer(ModelSerializer):
    data = JSONSerializerField()

    class Meta:
        model = Score
        fields = "__all__"


class NewImportSerializer(serializers.Serializer):
    period = serializers.CharField()
