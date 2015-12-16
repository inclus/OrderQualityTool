from rest_framework.relations import StringRelatedField
from rest_framework.serializers import ModelSerializer

from dashboard.models import FacilityCycleRecordScore, FacilityCycleRecord
from locations.models import Facility


class FacilitySerializer(ModelSerializer):
    warehouse = StringRelatedField()
    ip = StringRelatedField()
    district = StringRelatedField()

    class Meta:
        model = Facility


class FacilityScoreSerializer(ModelSerializer):
    class Meta:
        model = FacilityCycleRecordScore


class FacilityCycleRecordSerializer(ModelSerializer):
    scores = FacilityScoreSerializer(many=True)
    facility = FacilitySerializer()

    class Meta:
        model = FacilityCycleRecord
