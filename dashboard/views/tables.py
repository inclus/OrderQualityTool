import csv
import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic import View
from django_datatables_view.base_datatable_view import BaseDatatableView
from pydash import py_

from dashboard.checks.builder import FACILITY_TWO_GROUPS_WITH_SAMPLE
from dashboard.checks.check import get_check_from_dict
from dashboard.checks.tracer import Tracer
from dashboard.helpers import *
from dashboard.models import Score, FacilityTest, TracingFormulations


class ScoresTableView(BaseDatatableView):
    model = Score

    def get_order_columns(self):
        return self.get_columns()

    def get_columns(self):
        check_columns = py_(FacilityTest.objects.all()).map(lambda check: check.name).value()
        columns = [NAME, DISTRICT.lower(), WAREHOUSE.lower(), IP.lower()]
        columns.extend(check_columns)
        return columns

    def prepare_results(self, qs):
        data = []
        for item in qs:
            row = [self.render_column(item, column) for column in self.get_columns()]
            row.append(item.id)
            data.append(row)
        return data

    def render_column(self, row, column):
        display_text = {YES: PASS, NO: FAIL, NOT_REPORTING: N_A}
        all_checks = FacilityTest.objects.all()
        default_columns = py_(all_checks).reject(lambda check: check.get_type() == FACILITY_TWO_GROUPS_WITH_SAMPLE).map(
            lambda check: check.name).value()
        formulation_columns = py_(all_checks).filter(
            lambda check: check.get_type() == FACILITY_TWO_GROUPS_WITH_SAMPLE
        ).map(
            lambda check: check.name).value()

        formulation = self.request.POST.get(FORMULATION, F1)
        if column in default_columns:
            value_for_column = self.get_check_result(column, row)
            if type(value_for_column) == dict and DEFAULT in value_for_column:
                actual_result = value_for_column[DEFAULT]
                return display_text[actual_result] if actual_result else actual_result
            else:
                return ""
        elif column in formulation_columns:
            result = self.get_check_result(column, row)
            if type(result) == dict and formulation in result:
                actual_result = result[formulation]
                return display_text[actual_result] if actual_result else actual_result
            else:
                return ""
        else:
            return super(ScoresTableView, self).render_column(row, column)

    def get_check_result(self, column, row):
        if type(row.data) is dict:
            return row.data.get(column)
        return ""

    def get_initial_queryset(self):
        qs = super(ScoresTableView, self).get_initial_queryset()
        cycle = self.request.POST.get(u'cycle', None)
        district_filter = self.request.POST.get(u'district', None)
        ip = self.request.POST.get(u'ip', None)
        warehouse = self.request.POST.get(u'warehouse', None)
        filters = {}
        if cycle:
            filters['cycle'] = cycle
        if district_filter:
            districts = district_filter.split(',')
            filters['district__in'] = districts
        if ip:
            filters['ip'] = ip
        if warehouse:
            filters['warehouse'] = warehouse

        if self.request.user:
            if self.request.user.access_level and self.request.user.access_area:
                filters[self.request.user.access_level.lower()] = self.request.user.access_area

        qs = qs.filter(**filters)
        return qs

    def filter_queryset(self, qs):
        search = self.request.POST.get(u'search[value]', None)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(district__icontains=search) | Q(ip__icontains=search) | Q(
                warehouse__icontains=search))
        return qs


class ScoreDetailsView(View):
    def get_context_data(self, request, id, column):
        scores = {YES: "Pass", NO: "Fail", NOT_REPORTING: "N/A"}
        combination = request.GET.get('combination', DEFAULT)
        combination_name = combination
        if combination != DEFAULT:
            tracers = TracingFormulations.objects.filter(slug=combination)
            if len(tracers) > 0:
                combination_name = tracers[0].name
        column = int(column)
        score = Score.objects.get(id=id)
        score_data = {'ip': score.ip, 'district': score.district, 'warehouse': score.warehouse, 'name': score.name,
                      'cycle': score.cycle, 'combination': combination_name}
        has_result = column > 3
        response_data = {'score': score_data, 'has_result': has_result}
        template_name = "check/base.html"
        if has_result:
            check_obj = self.get_test_by_column(column)
            check = get_check_from_dict(json.loads(check_obj.definition))
            response_data['data'] = check.get_preview_data({'name': score.name, "district": score.district},
                                                           score.cycle, Tracer(key=combination))
            if score.data and type(score.data) is dict:
                result = score.data.get(check_obj.name)
            else:
                result = None
            # actual_result = get_actual_result(result, combination)
            result_data = {'name': check_obj.name, 'test': check_obj.short_description,
                           'result': scores.get(response_data['data']['result'][combination]),
                           'has_combination': len(maybe(result).or_else([])) > 1}
            response_data['result'] = result_data
        response_data['detail'] = {'id': id, 'column': column, 'test': score.name}
        return response_data, template_name, score, combination_name

    def get_test_by_column(self, column):
        return maybe(FacilityTest.objects.get(order=column - 3)).or_else(None)

    def get(self, request, id, column):
        response_data, template_name, score, combination = self.get_context_data(request, id, column)
        return render_to_response(template_name, context=response_data)


def results_as_array(response_data, score, combination):
    row = []
    name_row = [response_data['result']['name']]
    row.append([""])
    row.append(name_row)
    row.append([""])
    headers = ["Facility", "District", "Warehouse", "IP", "Cycle"]
    details = [score.name, score.district, score.warehouse, score.ip, score.cycle]
    if combination != DEFAULT:
        headers.append("Formulation")
        details.append(combination)
    headers.append("Result")
    details.append(response_data['result']['result'])
    row.append(headers)
    row.append(details)
    row.append([""])
    row.append([""])

    groups = response_data['data'].get('groups', [])
    if len(groups) > 0:
        for group in groups:
            row.append([""])
            row.append([group['name']])
            row.append([""])
            group_headers = ["Formulation"]
            group_headers.extend(group['headers'])
            row.append(group_headers)
            for value_row in group['values']:
                row.append(value_row)

        row.append([""])
        row.append([""])
        row.append(["Factored"])
        row.append([""])

        for group in groups:
            row.append([""])
            row.append([group['name']])
            row.append([""])
            group_headers = ["Formulation"]
            group_headers.extend(group['headers'])
            row.append(group_headers)
            for value_row in group['factored_values']:
                row.append(value_row)
    return row


class ScoreDetailsCSVView(ScoreDetailsView):
    def get(self, request, id, column):
        response_data, template_name, score, combination = self.get_context_data(request, id, column)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s-%s.csv"' % (
            score.name, response_data['result']['name'])
        writer = csv.writer(response)

        writer.writerows(results_as_array(response_data, score, combination))
        return response


class TableCSVExportView(View):
    def parse_value(self, value):
        mapping = {YES: PASS, NO: FAIL, NOT_REPORTING: N_A}
        return mapping.get(value, value)

    def get(self, request):
        formulation = request.GET.get('formulation', Tracer.F1().key)
        cycle = request.GET.get('cycle', None)
        test_names = [test[0] for test in FacilityTest.objects.values_list("name")]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="facilitytable-%s-%s.csv"' % (cycle, formulation)
        writer = csv.writer(response)
        columns = ["Facility", "District", "Warehouse", "IP"]
        writer.writerow(columns + test_names)
        filter = {'cycle': cycle}
        if self.request.user:
            if self.request.user.access_level and self.request.user.access_area:
                filter[self.request.user.access_level.lower()] = self.request.user.access_area
        for score in Score.objects.filter(**filter).order_by('name'):
            row = [score.name, score.district, score.warehouse, score.ip]
            for c in test_names:
                value = score.data.get(c)
                if type(value) is dict:
                    if DEFAULT in value:
                        row.append(self.parse_value(value.get(DEFAULT)))
                    else:
                        row.append(self.parse_value(value.get(formulation)))
                else:
                    row.append(value)
            writer.writerow(row)

        return response
