import csv
import os

import django_filters
from arrow import now
from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Count, Case, When, Avg
from django.http import HttpResponse
from django.views.generic import TemplateView, FormView
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView

from dashboard.forms import FileUploadForm
from dashboard.helpers import generate_cycles, ORDER_FORM_FREE_OF_GAPS, ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, DIFFERENT_ORDERS_OVER_TIME, to_date, CLOSING_BALANCE_MATCHES_OPENING_BALANCE, CONSUMPTION_AND_PATIENTS, STABLE_CONSUMPTION, WAREHOUSE_FULFILMENT, STABLE_PATIENT_VOLUMES, GUIDELINE_ADHERENCE, NNRTI_CURRENT_ADULTS, NNRTI_CURRENT_PAED, NNRTI_NEW_ADULTS, NNRTI_NEW_PAED, YES
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord, CycleTestScore, CycleFormulationTestScore
from dashboard.tasks import import_general_report
from locations.models import Facility, District, IP, WareHouse


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
                results.append({"cycle": cycle, "reporting": rate, "not_reporting": 100 - rate})
            else:
                results.append({"cycle": cycle, "reporting": 0, "not_reporting": 100})
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
                results.append({"cycle": cycle, "web": rate, "paper": 100 - rate})
            else:
                results.append({"cycle": cycle, "web": 0, "paper": 100})
        return Response({"values": results})


class FacilitiesMultipleReportingView(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in FacilityCycleRecord.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        cycle = request.GET.get('cycle', most_recent_cycle)
        records = FacilityCycleRecord.objects.filter(cycle=cycle, multiple=True).values('multiple', 'facility__name')
        return Response({"values": records})


class BestPerformingDistrictsView(APIView):
    reverse = True

    def get(self, request):
        results = self.get_data(request)
        return Response({"values": results})

    def get_data(self, request):
        filters = {}
        levels = {'district': District, 'ip': IP, 'warehouse': WareHouse, 'facility': Facility}
        cycle = request.GET.get('cycle', None)
        level = request.GET.get('level', 'district').lower()
        current_model = levels.get(level, District)
        if cycle:
            filters['facilities__records__cycle'] = cycle
            if level == 'facility':
                filters = {}
                filters['records__cycle'] = cycle

        if level == 'facility':
            data = current_model.objects.filter(**filters).values('name', 'records__cycle').annotate(count=Count('records__scores__pk'), yes=Count(Case(When(records__scores__score=YES, then=1))))
        else:
            data = current_model.objects.filter(**filters).values('name', 'facilities__records__cycle').annotate(count=Count('facilities__records__scores__pk'), yes=Count(Case(When(facilities__records__scores__score=YES, then=1))))
        for item in data:
            if item['yes'] == 0:
                item['rate'] = 0
            else:
                item['rate'] = (float(item['yes']) / float(item['count'])) * 100
        results = sorted(data, key=lambda x: (x['rate'], x['count']), reverse=self.reverse)
        return results


class WorstPerformingDistrictsView(BestPerformingDistrictsView):
    reverse = False


class BestPerformingDistrictsCSVView(BestPerformingDistrictsView):
    file_name = 'best'

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        level = request.GET.get('level', 'district').lower()
        response['Content-Disposition'] = 'attachment; filename="%s-%s.csv"' % (self.file_name, level)
        writer = csv.writer(response)
        writer.writerow([level, 'reporting rate'])
        results = self.get_data(request)
        for n in results:
            writer.writerow([n['name'], n['rate']])
        return response


class WorstPerformingDistrictsCSVView(BestPerformingDistrictsCSVView):
    file_name = 'worst'
    reverse = False


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
        cycles = generate_cycles(now().replace(years=-2), month)
        cycles.reverse()
        return Response({"values": cycles, "most_recent_cycle": most_recent_cycle})


class ReportMetrics(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in FacilityCycleRecord.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        web = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.filter(cycle=most_recent_cycle).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(web_based=True, then=1)))))
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in FacilityCycleRecord.objects.filter(cycle=most_recent_cycle).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(reporting_status=True, then=1)))))
        item = web.get(most_recent_cycle)
        report_item = data.get(most_recent_cycle)
        web_rate = "{0:.1f}".format((float(item['reporting']) / float(item['count'])) * 100)
        report_rate = "{0:.1f}".format((float(report_item['reporting']) / float(report_item['count'])) * 100)
        adherence = "{0:.1f}".format(CycleFormulationTestScore.objects.filter(test=GUIDELINE_ADHERENCE, cycle=cycle['cycle']).aggregate(adherence=Avg('yes')).get("adherence", 0))
        return Response({"webBased": web_rate, "reporting": report_rate, "adherence": adherence})


class OrderFormFreeOfGapsView(APIView):
    test = ORDER_FORM_FREE_OF_GAPS

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
        scores = CycleTestScore.objects.filter(test=self.test, **filters)
        data = dict((k.cycle, k) for k in scores)
        results = []
        for cycle in cycles:
            if cycle in data:
                item = data.get(cycle)
                results.append({"cycle": cycle, "yes": item.yes, "no": item.no, "not_reporting": item.not_reporting})
            else:
                results.append({"cycle": cycle, "rate": 0, "yes": 0, "no": 0, "not_reporting": 0})
        return Response({'values': results})


class RegimensListView(APIView):
    def get(self, request):
        values = FacilityConsumptionRecord.objects.order_by().values('formulation').distinct()
        return Response({'values': values})


class OrderFormFreeOfNegativeNumbersView(APIView):
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS

    def get(self, request):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        formulation = request.GET.get('regimen', None)
        filters = {'formulation__icontains': formulation}
        cycles = generate_cycles(now().replace(years=-2), now())
        if start and end:
            start_index = cycles.index(start)
            end_index = cycles.index(end)
            cycles_included = cycles[start_index: end_index + 1]
            cycles = cycles_included
            filters['cycle__in'] = cycles_included
        scores = CycleFormulationTestScore.objects.filter(test=self.test, **filters)
        data = dict((k.cycle, k) for k in scores)
        results = []
        for cycle in cycles:
            if cycle in data:
                item = data.get(cycle)
                results.append({"cycle": cycle, "yes": item.yes, "no": item.no, "not_reporting": item.not_reporting})
            else:
                results.append({"cycle": cycle, "rate": 0, "yes": 0, "no": 0, "not_reporting": 0})
        return Response({'values': results})


class DifferentOrdersOverTimeView(OrderFormFreeOfNegativeNumbersView):
    test = DIFFERENT_ORDERS_OVER_TIME


class ClosingBalanceView(DifferentOrdersOverTimeView):
    test = CLOSING_BALANCE_MATCHES_OPENING_BALANCE


class ConsumptionAndPatientsView(DifferentOrdersOverTimeView):
    test = CONSUMPTION_AND_PATIENTS


class StableConsumptionView(DifferentOrdersOverTimeView):
    test = STABLE_CONSUMPTION


class WarehouseFulfilmentView(DifferentOrdersOverTimeView):
    test = WAREHOUSE_FULFILMENT


class StablePatientVolumesView(DifferentOrdersOverTimeView):
    test = STABLE_PATIENT_VOLUMES


class GuideLineAdherenceView(DifferentOrdersOverTimeView):
    test = GUIDELINE_ADHERENCE


class NNRTICurrentAdultsView(OrderFormFreeOfGapsView):
    test = NNRTI_CURRENT_ADULTS


class NNRTICurrentPaedView(OrderFormFreeOfGapsView):
    test = NNRTI_CURRENT_PAED


class NNRTINewAdultsView(OrderFormFreeOfGapsView):
    test = NNRTI_NEW_ADULTS


class NNRTINewPaedView(OrderFormFreeOfGapsView):
    test = NNRTI_NEW_PAED
