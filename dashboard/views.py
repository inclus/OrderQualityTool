import os

import django_filters
from arrow import now
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Count, Case, When
from django.views.generic import TemplateView, FormView
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord
from dashboard.tasks import import_general_report
from forms import FileUploadForm, generate_cycles
from locations.models import Facility, District


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
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


class FacilitySerializer(ModelSerializer):
    class Meta:
        model = Facility


class FacilityCycleRecordSerializer(ModelSerializer):
    facility = FacilitySerializer()

    class Meta:
        model = FacilityCycleRecord


class FacilityConsumptionRecordSerializer(ModelSerializer):
    facility_cycle = FacilityCycleRecordSerializer()

    class Meta:
        model = FacilityConsumptionRecord


class CycleRecordsListView(ListAPIView):
    queryset = FacilityCycleRecord.objects.all()
    serializer_class = FacilityCycleRecordSerializer


class ConsumptionRecordListView(ListAPIView):
    queryset = FacilityConsumptionRecord.objects.all()
    serializer_class = FacilityConsumptionRecordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = FacilityConsumptionRecordFilter


class FacilitiesReportingView(APIView):
    def get(self, request):
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(reporting_status=True, then=1)))))
        cycles = generate_cycles(now().replace(years=-2), now())
        results = []
        for cycle in cycles:
            if cycle in data:
                item = data.get(cycle)
                rate = (float(item['reporting']) / float(item['count'])) * 100
                results.append({"cycle": cycle, "rate": rate})
            else:
                results.append({"cycle": cycle, "rate": 0})
        return Response({"values": results})


class WebBasedReportingView(APIView):
    def get(self, request):
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(web_based=True, then=1)))))
        cycles = generate_cycles(now().replace(years=-2), now())
        results = []
        for cycle in cycles:
            if cycle in data:
                item = data.get(cycle)
                rate = (float(item['reporting']) / float(item['count'])) * 100
                results.append({"cycle": cycle, "rate": rate})
            else:
                results.append({"cycle": cycle, "rate": 0})
        return Response({"values": results})


class BestPerformingDistrictsView(APIView):
    reverse = True

    def get(self, request):
        filters = {}
        cycle = request.GET.get('cycle', None)
        if cycle:
            filters['facilities__records__cycle'] = cycle
        data = District.objects.filter(**filters).values('name', 'facilities__records__cycle').annotate(count=Count('facilities__records__pk'), reporting=Count(Case(When(facilities__records__reporting_status=True, then=1))))
        for item in data:
            if item['reporting'] == 0:
                item['rate'] = 0
            else:
                item['rate'] = (float(item['reporting']) / float(item['count'])) * 100
        results = sorted(data, key=lambda x: (x['rate'], x['count']), reverse=self.reverse)[:10]
        return Response({"values": results})


class WorstPerformingDistrictsView(BestPerformingDistrictsView):
    reverse = False


class CyclesView(APIView):
    def get(self, request):
        return Response({"values": generate_cycles(now().replace(years=-2), now())})
