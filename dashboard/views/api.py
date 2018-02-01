import csv
import json
from functools import cmp_to_key

import pydash
import pygogo
from braces.views import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.db.models import Count, Sum
from django.db.models.expressions import F
from django.forms import model_to_dict
from django.http import HttpResponse
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.checks.check_builder import FACILITY_TWO_GROUPS_WITH_SAMPLE
from dashboard.helpers import *
from dashboard.models import Score, WAREHOUSE, DISTRICT, MultipleOrderFacility, Cycle, MOH_CENTRAL, Consumption, \
    AdultPatientsRecord, PAEDPatientsRecord, FacilityTest, TracingFormulations
from dashboard.serializers import ScoreSerializer, NewImportSerializer
from dashboard.tasks import import_data_from_dhis2


def aggregate_scores(user, test, cycles, formulation, keys, count_values, filters):
    scores_filter = {}
    if user:
        access_level = user.access_level
        access_area = user.access_area
        if access_level and access_area:
            scores_filter[access_level.lower()] = access_area
    if user.is_superuser:
        scores_filter = filters
    score_objects = Score.objects.filter(**scores_filter).values("data", "cycle")
    grouped_objects = pydash.group_by(score_objects, lambda x: x["cycle"])

    def get_count_key(value):
        value_as_dict = json.loads(value.get('data'))
        return value_as_dict.get(test, {}).get(formulation, None) if type(value_as_dict) is dict else None

    def agg(value):
        values = grouped_objects.get(value, [])
        result = {'cycle': value}
        total = len(values)
        yes_count_value = count_values[YES]
        no_count_value = count_values[NO]
        not_reporting_count_value = count_values[NOT_REPORTING]
        if total > 0:
            counts = pydash.count_by(values, get_count_key)
            yes_count = counts.get(yes_count_value, 0)
            no_count = counts.get(no_count_value, 0)
            not_reporting_count = counts.get(not_reporting_count_value, 0)
            result[keys[YES]] = (yes_count * 100 / float(total))
            result[keys[NO]] = (no_count * 100 / float(total))
            result[keys[NOT_REPORTING]] = (not_reporting_count * 100 / float(total))
        else:
            result[keys[YES]] = 0
            result[keys[NO]] = 0
            result[keys[NOT_REPORTING]] = 0
        return result

    return pydash.collect(cycles, agg)


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
        most_recent_cycle = get_most_recent_cycle(Cycle, 'title')
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
                                                                              best=Sum(F(fm['pass']) + F(
                                                                                  'default_pass_count')),
                                                                              worst=Sum(F(fm['fail']) + F(
                                                                                  'default_fail_count')))

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
        most_recent_cycle = get_most_recent_cycle()
        if most_recent_cycle:
            month = to_date(most_recent_cycle)
            cycles = generate_cycles(now().replace(years=-2), month)
            cycles.reverse()
            return Response({"values": cycles, "most_recent_cycle": most_recent_cycle})
        return Response({"values": [], "most_recent_cycle": most_recent_cycle})


def get_most_recent_cycle(model=Score, field='cycle'):
    records = [cycle[field] for cycle in model.objects.values(field).distinct()]
    sorted_cyles = sorted(records, key=cmp_to_key(sort_cycle), reverse=True)
    if len(sorted_cyles) > 0:
        most_recent_cycle, = sorted_cyles[:1]
        return most_recent_cycle


def add_item_to_filter(name, value, filter):
    if value is not None and "all %s" % name not in value.lower():
        filter[name] = value


def build_filters(request):
    district = request.GET.get("district", None)
    ip = request.GET.get("ip", None)
    warehouse = request.GET.get("warehouse", None)
    filters = {}
    add_item_to_filter("district", district, filters)
    add_item_to_filter("ip", ip, filters)
    add_item_to_filter("warehouse", warehouse, filters)
    return filters


def prepare_for_ui(regimens):
    def for_each_item(item):
        new_item = {"name": item["name"], "id": item["id"]}
        definition = json.loads(maybe(item)["definition"].or_else("{}"))
        new_item["sampled"] = maybe(definition)['type']['id'].or_else("") == FACILITY_TWO_GROUPS_WITH_SAMPLE
        new_item["regimens"] = regimens
        return new_item

    return for_each_item


class GetTestsAPIView(APIView):
    def get(self, request):
        featured_tests = FacilityTest.objects.filter(featured=True).order_by('order').values('id', 'name', 'order',
                                                                                             'definition')[:2]
        ids_for_featured_tests = [item['id'] for item in featured_tests]
        other_tests = FacilityTest.objects.exclude(id__in=ids_for_featured_tests).order_by('order').values('id',
                                                                                                           'name',
                                                                                                           'order',
                                                                                                           'definition')
        regimens = TracingFormulations.objects.filter(model="Consumption").values('name')
        featured = pydash.py_(featured_tests).map(prepare_for_ui(regimens)).value()
        other = pydash.py_(other_tests).map(prepare_for_ui(regimens)).value()
        return Response({'featured': featured, 'other': other})


class ScoresAPIView(APIView):
    def generate_data(self, test, start, end, formulation=DEFAULT,
                      keys={YES: YES, NO: NO, NOT_REPORTING: NOT_REPORTING},
                      count_values={YES: YES, NO: NO, NOT_REPORTING: NOT_REPORTING}):
        filters = build_filters(self.request)
        if formulation is None:
            formulation = DEFAULT
        cycles = generate_cycles(now().replace(years=-2), now())
        if start and end:
            start_index = cycles.index(start)
            end_index = cycles.index(end)
            cycles_included = cycles[start_index: end_index + 1]
            cycles = cycles_included
        results = aggregate_scores(self.request.user, test, cycles, formulation, keys, count_values, filters)
        return Response({'values': results})

    def get(self, request, id):
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        regimen = request.GET.get('regimen', None)
        keys = {YES: 'yes', NO: 'no', NOT_REPORTING: 'not_reporting'}
        test = FacilityTest.objects.get(id=id)
        return self.generate_data(test.name, start, end, regimen, keys)


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


class AdminAccessView(APIView):
    def get(self, request):
        is_admin = type(request.user) != AnonymousUser and (
                request.user.access_level == MOH_CENTRAL or request.user.is_superuser)
        return Response({"is_admin": is_admin})


logger = pygogo.Gogo(__name__).get_structured_logger()


class NewImportView(APIView):
    def post(self, request):
        serializer = NewImportSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("launching task",
                        extra={"task_name": "import_data_from_dhis2", "period": serializer.data["period"]})
            import_data_from_dhis2.apply_async(args=[serializer.data["period"]], priority=2)
            return Response({"ok": True})
        return Response({"ok": False})


class ListAdultFormulations(APIView):
    def get(self, request):
        all_values = []
        distinct_values_from_adult = AdultPatientsRecord.objects.order_by().values_list('formulation').distinct()
        all_values.extend(distinct_values_from_adult)
        return Response({"values": pydash.chain(all_values).flatten().uniq().sort().value()})


class ListPaedFormulations(APIView):
    def get(self, request):
        all_values = []
        distinct_values_from_paed = PAEDPatientsRecord.objects.order_by().values_list('formulation').distinct()
        all_values.extend(distinct_values_from_paed)
        return Response({"values": pydash.chain(all_values).flatten().uniq().sort().value()})


class ListConsumptionFormulations(APIView):
    def get(self, request):
        all_values = []
        distinct_values_from_consumption = Consumption.objects.order_by().values_list('formulation').distinct()
        all_values.extend(distinct_values_from_consumption)
        return Response({"values": pydash.chain(all_values).flatten().uniq().sort().value()})


class ListPatientFields(APIView):
    def get(self, request):
        all_fields = []
        fields_from_adult = model_to_dict(AdultPatientsRecord()).keys()
        fields_from_paed = model_to_dict(PAEDPatientsRecord()).keys()
        all_fields.extend(fields_from_adult)
        all_fields.extend(fields_from_paed)
        return Response(
            {"values": pydash.chain(all_fields).without(
                "id", "ip", "formulation", "warehouse", "notes", "name", "district",
                "cycle").uniq().sort().value()})


class ListConsumptionFields(APIView):
    def get(self, request):
        fields = model_to_dict(Consumption()).keys()
        return Response(
            {"values": pydash.chain(fields).without(
                "id", "ip", "formulation", "warehouse", "notes", "name", "district",
                "cycle").uniq().sort().value()})
