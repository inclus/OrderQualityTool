from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.views.serializers import DefinitionSerializer, DefinitionSampleSerializer


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
        from dashboard.models import TracingFormulations
        tracers = [{"name": tracer.name, "formulations": tracer.formulations} for tracer in
                   TracingFormulations.objects.filter(model=self.model)]
        return Response(data=tracers)


class PatientTracingFormulationView(ConsumptionTracingFormulationView):
    model = "Patients"
