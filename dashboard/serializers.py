import json

from rest_framework import serializers
from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from dashboard.models import Score, Cycle
from locations.models import Facility


class FacilitySerializer(ModelSerializer):
    warehouse = StringRelatedField()
    ip = StringRelatedField()
    district = StringRelatedField()

    class Meta:
        model = Facility


class FacilityScoreSerializer(ModelSerializer):
    class Meta:
        model = Score


class FacilityCycleRecordSerializer(ModelSerializer):
    scores = FacilityScoreSerializer(many=True)
    facility = FacilitySerializer()

    class Meta:
        model = Cycle


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value

class ScoreSerializer(ModelSerializer):
    REPORTING = JSONSerializerField()
    WEB_BASED = JSONSerializerField()
    MULTIPLE_ORDERS = JSONSerializerField()
    OrderFormFreeOfGaps = JSONSerializerField()
    guidelineAdherenceAdult1L = JSONSerializerField()
    guidelineAdherenceAdult2L = JSONSerializerField()
    guidelineAdherencePaed1L = JSONSerializerField()
    nnrtiNewPaed = JSONSerializerField()
    nnrtiCurrentPaed = JSONSerializerField()
    nnrtiNewAdults = JSONSerializerField()
    nnrtiCurrentAdults = JSONSerializerField()
    stablePatientVolumes = JSONSerializerField()
    consumptionAndPatients = JSONSerializerField()
    warehouseFulfilment = JSONSerializerField()
    differentOrdersOverTime = JSONSerializerField()
    closingBalanceMatchesOpeningBalance = JSONSerializerField()
    orderFormFreeOfNegativeNumbers = JSONSerializerField()
    stableConsumption = JSONSerializerField()

    class Meta:
        model = Score
