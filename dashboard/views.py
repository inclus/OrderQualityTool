import os

import django_filters
from arrow import now
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Count
from django.views.generic import TemplateView, FormView
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from dashboard.models import FacilityCycleRecord, DrugFormulation, FacilityConsumptionRecord
from dashboard.tasks import import_general_report
from forms import FileUploadForm, generate_cycles
from locations.models import Location


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        cycles = FacilityCycleRecord.objects.values('cycle').annotate(count=Count('facility'))
        locations_at_level_5 = Location.objects.filter(level=5).count()
        context['cycles'] = cycles
        context['location_count'] = locations_at_level_5
        return context


class DataImportView(LoginRequiredMixin, FormView):
    template_name = "import.html"
    form_class = FileUploadForm
    success_url = '/'

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        cycle = form.cleaned_data['cycle']
        path = default_storage.save('tmp/workspace.xlsx', ContentFile(import_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        import_general_report.delay(tmp_file, cycle)
        messages.add_message(self.request, messages.INFO, 'Successfully started import for cycle %s' % (cycle))
        return super(DataImportView, self).form_valid(form)


class FacilityConsumptionRecordFilter(django_filters.FilterSet):
    class Meta:
        model = FacilityConsumptionRecord
        fields = ['facility_cycle__facility']


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location


class FacilityCycleRecordSerializer(ModelSerializer):
    facility = LocationSerializer()

    class Meta:
        model = FacilityCycleRecord


class DrugFormulationSerializer(ModelSerializer):
    class Meta:
        model = DrugFormulation


class FacilityConsumptionRecordSerializer(ModelSerializer):
    facility_cycle = FacilityCycleRecordSerializer()

    class Meta:
        model = FacilityConsumptionRecord


class CycleRecordsListView(ListAPIView):
    queryset = FacilityCycleRecord.objects.all()
    serializer_class = FacilityCycleRecordSerializer


class DrugFormulationListView(ListAPIView):
    queryset = DrugFormulation.objects.all()
    serializer_class = DrugFormulationSerializer


class ConsumptionRecordListView(ListAPIView):
    queryset = FacilityConsumptionRecord.objects.all()
    serializer_class = FacilityConsumptionRecordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = FacilityConsumptionRecordFilter


class FacilitiesReportingView(APIView):
    def get(self, request):
        data = dict((record['cycle'], record['count']) for record in FacilityCycleRecord.objects.values('cycle').annotate(count=Count('facility')))
        cycles = generate_cycles(now().replace(years=-2), now())
        print data
        results = []
        for cycle in cycles:
            if cycle in data:
                results.append({"cycle": cycle, "count": data.get(cycle)})
            else:
                results.append({"cycle": cycle, "count": 0})
        return Response({"values": results})
