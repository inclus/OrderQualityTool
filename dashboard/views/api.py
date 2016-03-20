import csv
from functools import cmp_to_key
import pydash

from arrow import now
from braces.views import LoginRequiredMixin
from django.db.models import Count, Sum
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models.expressions import F

from dashboard.helpers import generate_cycles, to_date, GUIDELINE_ADHERENCE, ORDER_FORM_FREE_OF_GAPS, \
    ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, DIFFERENT_ORDERS_OVER_TIME, CLOSING_BALANCE_MATCHES_OPENING_BALANCE, \
    CONSUMPTION_AND_PATIENTS, STABLE_CONSUMPTION, WAREHOUSE_FULFILMENT, STABLE_PATIENT_VOLUMES, NNRTI_CURRENT_ADULTS, \
    NNRTI_CURRENT_PAED, NNRTI_NEW_ADULTS, NNRTI_NEW_PAED, sort_cycle, WEB_BASED, REPORTING, F1, F2, F3, DEFAULT, YES, NO, NOT_REPORTING

from dashboard.models import CycleFormulationScore, Score, WAREHOUSE, DISTRICT, MultipleOrderFacility, Cycle
from dashboard.serializers import ScoreSerializer

class BestPerformingDistrictsView(APIView):
    reverse = True
    acc = 'best'

    def get(self, request):
        results = self.get_data(request)
        return Response({"values": results})

    def get_data(self, request):
        filters = {}
        levels = {'district': 'district', 'ip': 'ip', 'warehouse': 'warehouse', 'facility': 'name'}
        formulation = request.GET.get('formulation', F1)
        level = request.GET.get('level', 'district').lower()
        name = levels.get(level, 'district')
        records = [cycle['title'] for cycle in Cycle.objects.values('title').distinct()]
        cycles = sorted(records, key=cmp_to_key(sort_cycle), reverse=True)[:1]
        most_recent_cycle = cycles[0] if len(cycles) > 0 else None
        cycle = request.GET.get('cycle', most_recent_cycle)

        if cycle:
            filters['cycle'] = cycle

        mapping = {
            F1: {"pass": "f1_pass_count", "fail": "f1_fail_count"},
            F2: {"pass": "f2_pass_count", "fail": "f2_fail_count"},
            F3: {"pass": "f3_pass_count", "fail": "f3_fail_count"},
        }

        fm = mapping.get(formulation, mapping.get(F1))
        data = Score.objects.filter(**filters).values(name, 'cycle').annotate(count=Count('pk'),
                                                                              best=Sum(F(fm['pass']) + F('default_pass_count')),
                                                                              worst=Sum(F(fm['fail']) + F('default_fail_count')))

        for item in data:
            item['name'] = item[name]
            item['rate'] = (float(item[self.acc]) / float(item['count']))
        results = sorted(data, key=lambda x: (x['rate'], x[self.acc]), reverse=True)
        return results


class WorstPerformingDistrictsView(BestPerformingDistrictsView):
    reverse = False
    acc = 'worst'


class BestPerformingDistrictsCSVView(BestPerformingDistrictsView):
    file_name = 'best'
    title = 'Average Number of Passes'

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        level = request.GET.get('level', 'district').lower()
        response['Content-Disposition'] = 'attachment; filename="%s-%s.csv"' % (self.file_name, level)
        writer = csv.writer(response)
        writer.writerow([level, self.title])
        results = self.get_data(request)
        for n in results:
            writer.writerow([n['name'], n['rate']])
        return response


class WorstPerformingDistrictsCSVView(BestPerformingDistrictsCSVView):
    file_name = 'worst'
    reverse = False
    acc = 'worst'
    title = 'Average Number of Fails'


class CyclesView(APIView):
    def get(self, request):
        records = [cycle['cycle'] for cycle in Score.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, key=cmp_to_key(sort_cycle), reverse=True)[:1]
        month = to_date(most_recent_cycle)
        cycles = generate_cycles(now().replace(years=-2), month)
        cycles.reverse()
        return Response({"values": cycles, "most_recent_cycle": most_recent_cycle})


class ReportMetrics(APIView):
    def get(self, request):
        adh = self.request.GET.get("adh", None)
        records = [cycle['cycle'] for cycle in CycleFormulationScore.objects.values('cycle').distinct()]
        most_recent_cycle, = sorted(records, key=cmp_to_key(sort_cycle), reverse=True)[:1]
        web_score = CycleFormulationScore.objects.get(cycle=most_recent_cycle, test=WEB_BASED, combination='DEFAULT')
        report_score = CycleFormulationScore.objects.get(cycle=most_recent_cycle, test=REPORTING, combination='DEFAULT')
        adh_filter = GUIDELINE_ADHERENCE
        if adh is not None:
            adh_filter = adh.replace(" ", "")
        adherence_qs = CycleFormulationScore.objects.filter(cycle=most_recent_cycle,
                                                            test__icontains=adh_filter,
                                                            combination='DEFAULT')
        web_rate = "{0:.1f}".format(web_score.yes)
        report_rate = "{0:.1f}".format(report_score.yes)
        adherence = "{0:.1f}".format(adherence_qs[0].yes) if len(adherence_qs) > 0 else ""
        return Response({"webBased": web_rate, "reporting": report_rate, "adherence": adherence})


def generate_data(test, start, end, formulation=None, keys={YES: 'yes', NO: 'no', NOT_REPORTING: 'not_reporting'}):
    filters = {}
    if formulation is not None:
        filters = {'combination__icontains': formulation}
    cycles = generate_cycles(now().replace(years=-2), now())
    if start and end:
        start_index = cycles.index(start)
        end_index = cycles.index(end)
        cycles_included = cycles[start_index: end_index + 1]
        cycles = cycles_included
        filters['cycle__in'] = cycles_included
    scores = CycleFormulationScore.objects.filter(test=test, **filters)
    data = dict((k.cycle, k) for k in scores)
    results = []
    for cycle in cycles:
        if cycle in data:
            item = data.get(cycle)
            results.append({"cycle": cycle, keys.get(YES): item.yes, keys.get(NO): item.no, keys.get(NOT_REPORTING): item.not_reporting})
        else:
            results.append({"cycle": cycle, "rate": None, keys.get(YES): None, keys.get(NO): None, keys.get(NOT_REPORTING): None})
    return Response({'values': results})


class FacilitiesReportingView(APIView):
    test = REPORTING

    def get(self, request):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        keys = {YES: 'reporting', NO: 'not_reporting', NOT_REPORTING: 'n_a'}
        return generate_data(self.test, start, end, None, keys)


class WebBasedReportingView(APIView):
    test = WEB_BASED

    def get(self, request):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        keys = {YES: 'web', NO: 'paper', NOT_REPORTING: 'not_reporting'}
        return generate_data(self.test, start, end, None, keys)


class FacilitiesMultipleReportingView(APIView):
    def get(self, request):
        cycles = [cycle['cycle'] for cycle in MultipleOrderFacility.objects.values('cycle').distinct()]
        sorted_cycles = sorted(cycles, key=cmp_to_key(sort_cycle), reverse=True)
        most_recent_cycle = sorted_cycles[0]
        cycle = request.GET.get('cycle', most_recent_cycle)
        records = MultipleOrderFacility.objects.filter(cycle=cycle).order_by('name').values('name', 'district', 'ip', 'warehouse')
        return Response({"values": records})


class OrderFormFreeOfGapsView(APIView):
    test = ORDER_FORM_FREE_OF_GAPS

    def get(self, request):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        return generate_data(self.test, start, end)


class OrderFormFreeOfNegativeNumbersView(APIView):
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS

    def get(self, request):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        formulation = request.GET.get('regimen', None)
        return generate_data(self.test, start, end, formulation)


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

    def get(self, request):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        formulation = request.GET.get('regimen', None)
        filters = {'combination__icontains': 'DEFAULT'}
        cycles = generate_cycles(now().replace(years=-2), now())
        if start and end:
            start_index = cycles.index(start)
            end_index = cycles.index(end)
            cycles_included = cycles[start_index: end_index + 1]
            cycles = cycles_included
            filters['cycle__in'] = cycles_included

        test_name = "%s%s" % (self.test, formulation.replace(" ", ""))
        scores = CycleFormulationScore.objects.filter(test=test_name, **filters)
        data = dict((k.cycle, k) for k in scores)
        results = []
        for cycle in cycles:
            if cycle in data:
                item = data.get(cycle)
                results.append({"cycle": cycle, "yes": item.yes, "no": item.no, "not_reporting": item.not_reporting})
            else:
                results.append({"cycle": cycle, "rate": None, "yes": None, "no": None, "not_reporting": None})
        return Response({'values': results})


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
        ips = Score.objects.values('ip').order_by('ip').distinct()
        warehouses = Score.objects.values('warehouse').order_by('warehouse').distinct()
        districts = Score.objects.values('district').order_by('district').distinct()
        cycles = Score.objects.values('cycle').distinct()
        return Response({"ips": ips, "warehouses": warehouses, "districts": districts, "cycles": cycles})


class FacilityTestCycleScoresListView(ListAPIView):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('cycle', 'name', 'ip', 'warehouse', 'district')


class RankingsAccessView(LoginRequiredMixin, APIView):
    def get(self, request):
        levels = ['District', 'Warehouse', 'IP', 'Facility']
        if request.user.access_level == "IP":
            levels = ['District', 'Warehouse', 'Facility']
        if request.user.access_level == WAREHOUSE:
            levels = ['District', 'IP', 'Facility']
        if request.user.access_level == DISTRICT:
            levels = ['IP', 'Warehouse', 'Facility']
        return Response({"values": levels})


class AccessAreasView(APIView):
    def get(self, request):
        level = request.GET.get('level', None)
        access_levels = ['district', 'warehouse', 'ip', 'facility']
        access_areas = []
        if level and level.lower() in access_levels:
            access_areas = pydash.reject(Score.objects.values_list(level, flat=True).distinct(), lambda x: len(x) < 1)
        return Response(access_areas)
