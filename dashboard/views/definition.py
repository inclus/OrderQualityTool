from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.views.serializers import DefinitionSampleSerializer, DefinitionSerializer


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


class TracingFormulationView(APIView):

    def get(self, request):
        from dashboard.models import TracingFormulations
        tracers = [
            {"name": tracer.name, "slug": tracer.slug, "consumption_formulations": tracer.consumption_formulations,
             "patient_formulations": tracer.patient_formulations} for tracer in
            TracingFormulations.objects.all()]
        return Response(data=tracers)
