import math
import os

import arrow
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
from forms import FileUploadForm, generate_cycles, generate_cycles_numbered
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
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        filters = {}
        cycles = generate_cycles(now().replace(years=-2), now())
        if start and end:
            start_index = cycles.index(start)
            end_index = cycles.index(end)
            cycles_included = cycles[start_index: end_index + 1]
            cycles = cycles_included
            filters['cycle__in'] = cycles_included
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.filter(**filters).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(reporting_status=True, then=1)))))
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
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        filters = {}
        cycles = generate_cycles(now().replace(years=-2), now())
        if start and end:
            start_index = cycles.index(start)
            end_index = cycles.index(end)
            cycles_included = cycles[start_index: end_index + 1]
            cycles = cycles_included
            filters['cycle__in'] = cycles_included
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(web_based=True, then=1)))))
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


def to_date(text):
    month = text.split('-')[1].strip()
    return arrow.get(month, 'MMM YYYY')


def sort_cycle(item1, item2):
    if to_date(item1) < to_date(item2):
        return -1
    elif to_date(item1) > to_date(item2):
        return 1
    else:
        return 0


class CyclesView(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in FacilityCycleRecord.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        month = to_date(most_recent_cycle)
        cycle_number = int(math.ceil((float(month.format('MM')) / 12) * 6))
        return Response({"values": generate_cycles_numbered(now().replace(years=-2), month), "most_recent_cycle": {"name": most_recent_cycle, "number": cycle_number, "year": month.format('YY')}})


class ReportMetrics(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in FacilityCycleRecord.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        web = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.filter(cycle=most_recent_cycle).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(web_based=True, then=1)))))
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.filter(cycle=most_recent_cycle).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(reporting_status=True, then=1)))))
        item = web.get(most_recent_cycle)
        report_item = data.get(most_recent_cycle)
        web_rate = "{0:.2f}".format((float(item['reporting']) / float(item['count'])) * 100)
        report_rate = "{0:.2f}".format((float(report_item['reporting']) / float(report_item['count'])) * 100)
        return Response({"webBased": web_rate, "reporting": report_rate})


class BestPerformingWebDistrictsView(APIView):
    reverse = True

    def get(self, request):
        filters = {}
        cycle = request.GET.get('cycle', None)
        if cycle:
            filters['facilities__records__cycle'] = cycle
        data = District.objects.filter(**filters).values('name', 'facilities__records__cycle').annotate(count=Count('facilities__records__pk'), reporting=Count(Case(When(facilities__records__web_based=True, then=1))))
        for item in data:
            if item['reporting'] == 0:
                item['rate'] = 0
            else:
                item['rate'] = (float(item['reporting']) / float(item['count'])) * 100
        results = sorted(data, key=lambda x: (x['rate'], x['count']), reverse=self.reverse)[:10]
        return Response({"values": results})


class WorstPerformingWebDistrictsView(BestPerformingWebDistrictsView):
    reverse = False
