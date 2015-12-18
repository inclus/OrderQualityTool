import csv
import functools
import operator

from arrow import now
from braces.views import LoginRequiredMixin
from django.db.models import Count, Case, When, Avg, Q
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.helpers import generate_cycles, YES, to_date, GUIDELINE_ADHERENCE, ORDER_FORM_FREE_OF_GAPS, ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, DIFFERENT_ORDERS_OVER_TIME, CLOSING_BALANCE_MATCHES_OPENING_BALANCE, CONSUMPTION_AND_PATIENTS, STABLE_CONSUMPTION, WAREHOUSE_FULFILMENT, STABLE_PATIENT_VOLUMES, NNRTI_CURRENT_ADULTS, NNRTI_CURRENT_PAED, NNRTI_NEW_ADULTS, NNRTI_NEW_PAED, sort_cycle
from dashboard.models import Cycle, CycleFormulationScore, CycleScore, Consumption, Score, WAREHOUSE, DISTRICT
from dashboard.serializers import ScoreSerializer
from locations.models import District, IP, WareHouse


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
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in Cycle.objects.filter(**filters).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(reporting_status=True, then=1)))))
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
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in Cycle.objects.values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(web_based=True, then=1)))))
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
        records = [cycle['cycle'] for cycle in Cycle.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        cycle = request.GET.get('cycle', most_recent_cycle)
        records = Cycle.objects.filter(cycle=cycle, multiple=True).values('multiple', 'facility__name')
        return Response({"values": records})


class BestPerformingDistrictsView(APIView):
    reverse = True

    def get(self, request):
        results = self.get_data(request)
        return Response({"values": results})

    def get_data(self, request):
        filters = {}
        levels = {'district': 'district', 'ip': 'ip', 'warehouse': 'warehouse', 'facility': 'name'}
        cycle = request.GET.get('cycle', None)
        level = request.GET.get('level', 'district').lower()
        name = levels.get(level, 'district')

        if cycle:
            filters['cycle'] = cycle
        fields = [Q(nnrtiNewPaed=YES),
                  Q(stablePatientVolumes=YES),
                  Q(REPORTING=YES),
                  Q(consumptionAndPatients=YES),
                  Q(nnrtiCurrentPaed=YES),
                  Q(warehouseFulfilment=YES),
                  Q(differentOrdersOverTime=YES),
                  Q(closingBalanceMatchesOpeningBalance=YES),
                  Q(WEB_BASED=YES),
                  Q(OrderFormFreeOfGaps=YES),
                  Q(MULTIPLE_ORDERS=YES),
                  Q(nnrtiNewAdults=YES),
                  Q(orderFormFreeOfNegativeNumbers=YES),
                  Q(nnrtiCurrentAdults=YES),
                  Q(stableConsumption=YES),
                  Q(guidelineAdherenceAdultlL=YES),
                  Q(guidelineAdherenceAdult2L=YES),
                  Q(guidelineAdherencePaed1L=YES)
                  ]
        count_filters = functools.reduce(operator.or_, fields)
        data = Score.objects.filter(**filters).values(name, 'cycle').annotate(count=Count('pk'), yes=Count(Case(When(count_filters, then=1))))
        for item in data:
            item['name'] = item[name]
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


class CyclesView(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in Cycle.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        month = to_date(most_recent_cycle)
        cycles = generate_cycles(now().replace(years=-2), month)
        cycles.reverse()
        return Response({"values": cycles, "most_recent_cycle": most_recent_cycle})


class ReportMetrics(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in Cycle.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, sort_cycle, reverse=True)[:1]
        web = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in Cycle.objects.filter(cycle=most_recent_cycle).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(web_based=True, then=1)))))
        data = dict((record['cycle'], {'count': record['count'], 'reporting': record['reporting']}) for record in Cycle.objects.filter(cycle=most_recent_cycle).values('cycle').annotate(count=Count('pk'), reporting=Count(Case(When(reporting_status=True, then=1)))))
        item = web.get(most_recent_cycle)
        report_item = data.get(most_recent_cycle)
        web_rate = "{0:.1f}".format((float(item['reporting']) / float(item['count'])) * 100)
        report_rate = "{0:.1f}".format((float(report_item['reporting']) / float(report_item['count'])) * 100)
        adherence = "{0:.1f}".format(CycleFormulationScore.objects.filter(test=GUIDELINE_ADHERENCE, cycle=cycle['cycle']).aggregate(adherence=Avg('yes')).get("adherence", 0))
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
        scores = CycleScore.objects.filter(test=self.test, **filters)
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
        values = Consumption.objects.order_by().values('formulation').distinct()
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
        scores = CycleFormulationScore.objects.filter(test=self.test, **filters)
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


class FilterValuesView(APIView):
    def get(self, request):
        ips = IP.objects.values('pk', 'name').order_by('name').distinct()
        warehouses = WareHouse.objects.values('pk', 'name').order_by('name').distinct()
        districts = District.objects.values('pk', 'name').order_by('name').distinct()
        cycles = Cycle.objects.values('cycle').distinct()
        formulations = Score.objects.values('formulation').distinct()
        return Response({"ips": ips, "warehouses": warehouses, "districts": districts, "cycles": cycles, "formulations": formulations})


class FacilityTestCycleScoresListView(ListAPIView):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('cycle', 'name', 'ip', 'warehouse', 'district', 'formulation')


class RankingsAccessView(LoginRequiredMixin, APIView):
    def get(self, request):
        levels = ['District', 'Warehouse', 'IP', 'Facility']
        if request.user.access_level == "IP":
            levels = ['District', 'Warehouse', 'Facility']
        if request.user.access_level == WAREHOUSE:
            levels = ['District', 'IP', 'Facility']
        if request.user.access_level == DISTRICT:
            levels = ['District', 'Warehouse']
        return Response({"values": levels})
