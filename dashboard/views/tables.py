import csv

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.generic import View
from django_datatables_view.base_datatable_view import BaseDatatableView

from dashboard.helpers import *
from dashboard.models import Score
from dashboard.views.data_sources import NegativesCheckDataSource, ConsumptionAndPatientsDataSource, TwoCycleDataSource, \
    ClosingBalanceMatchesOpeningBalanceDataSource, StableConsumptionDataSource, StablePatientVolumesDataSource, \
    WarehouseFulfillmentDataSource, GuidelineAdherenceDataSource, NNRTIDataSource

TEST_DATA = {
    ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS: NegativesCheckDataSource,
    CONSUMPTION_AND_PATIENTS: ConsumptionAndPatientsDataSource,
    DIFFERENT_ORDERS_OVER_TIME: TwoCycleDataSource,
    CLOSING_BALANCE_MATCHES_OPENING_BALANCE: ClosingBalanceMatchesOpeningBalanceDataSource,
    STABLE_CONSUMPTION: StableConsumptionDataSource,
    STABLE_PATIENT_VOLUMES: StablePatientVolumesDataSource,
    WAREHOUSE_FULFILMENT: WarehouseFulfillmentDataSource,
    GUIDELINE_ADHERENCE_PAED_1L: GuidelineAdherenceDataSource,
    GUIDELINE_ADHERENCE_ADULT_2L: GuidelineAdherenceDataSource,
    GUIDELINE_ADHERENCE_ADULT_1L: GuidelineAdherenceDataSource,
    NNRTI_ADULTS: NNRTIDataSource,
    NNRTI_PAED: NNRTIDataSource
}

class ScoresTableView(BaseDatatableView):
    model = Score
    columns = [
        NAME,
        DISTRICT.lower(),
        WAREHOUSE.lower(),
        IP.lower(),
        REPORTING,
        GUIDELINE_ADHERENCE_ADULT_1L,
        GUIDELINE_ADHERENCE_ADULT_2L,
        GUIDELINE_ADHERENCE_PAED_1L,
        ORDER_FORM_FREE_OF_GAPS,
        MULTIPLE_ORDERS,
        ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS,
        CONSUMPTION_AND_PATIENTS,
        DIFFERENT_ORDERS_OVER_TIME,
        CLOSING_BALANCE_MATCHES_OPENING_BALANCE,
        STABLE_CONSUMPTION,
        STABLE_PATIENT_VOLUMES,
        WAREHOUSE_FULFILMENT,
        NNRTI_PAED,
        NNRTI_ADULTS,
    ]
    order_columns = columns

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([self.render_column(item, column) for column in self.get_columns()])
        return data

    def render_column(self, row, column):
        display_text = {YES: PASS, NO: FAIL, NOT_REPORTING: N_A}
        default_columns = [REPORTING,
                           MULTIPLE_ORDERS,
                           ORDER_FORM_FREE_OF_GAPS,
                           GUIDELINE_ADHERENCE_ADULT_1L,
                           GUIDELINE_ADHERENCE_ADULT_2L,
                           GUIDELINE_ADHERENCE_PAED_1L,
                           NNRTI_PAED,
                           NNRTI_ADULTS, ]
        formulation_columns = [STABLE_PATIENT_VOLUMES,
                               CONSUMPTION_AND_PATIENTS,
                               WAREHOUSE_FULFILMENT,
                               DIFFERENT_ORDERS_OVER_TIME,
                               CLOSING_BALANCE_MATCHES_OPENING_BALANCE,
                               ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS,
                               STABLE_CONSUMPTION]
        formulation = self.request.POST.get(FORMULATION, F1)
        if column in default_columns:
            value_for_column = getattr(row, column)
            if type(value_for_column) == dict and DEFAULT in value_for_column:
                actual_result = value_for_column[DEFAULT]
                return display_text[actual_result] if actual_result else actual_result
            else:
                return ""
        elif column in formulation_columns:
            result = getattr(row, column)
            if type(result) == dict and formulation in result:
                actual_result = result[formulation]
                return display_text[actual_result] if actual_result else actual_result
            else:
                return ""
        else:
            return super(ScoresTableView, self).render_column(row, column)

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
            qs = qs.filter(Q(name__icontains=search) | Q(district__icontains=search) | Q(ip__icontains=search) | Q(warehouse__icontains=search))
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            row = [self.render_column(item, column) for column in self.get_columns()]
            row.append(item.id)
            data.append(row)
        return data


class ScoreDetailsView(View):
    def get_context_data(self, request, id, column):
        scores = {YES: "Pass", NO: "Fail", NOT_REPORTING: "N/A"}
        combination = request.GET.get('combination', DEFAULT)
        column = int(column)
        score = Score.objects.get(id=id)
        score_data = {'ip': score.ip, 'district': score.district, 'warehouse': score.warehouse, 'name': score.name, 'cycle': score.cycle, 'combination': combination}
        has_result = column > 3
        response_data = {'score': score_data, 'has_result': has_result}
        template_name = "check/base.html"
        if has_result:
            view = ScoresTableView()
            test = view.columns[column]
            if test in TEST_DATA:
                data_source_class = TEST_DATA.get(test)
                data_source = data_source_class()
                template_name = data_source.get_template(test)
                response_data['data'] = data_source.load(score, test, combination)
            result = getattr(score, test, None)
            actual_result = get_actual_result(result, combination)
            result_data = {'test': TEST_NAMES.get(test, None), 'result': scores.get(actual_result), 'has_combination': len(result) > 1}
            response_data['result'] = result_data
        response_data['detail'] = {'id': id, 'column': column, 'test': score.name}
        return response_data, template_name, score, combination

    def get(self, request, id, column):
        response_data, template_name, score, combination = self.get_context_data(request, id, column)
        return render_to_response(template_name, context=response_data)

class ScoreDetailsCSVView(ScoreDetailsView):
    def get(self, request, id, column):
        view = ScoresTableView()
        test = view.columns[int(column)]
        response_data, template_name, score, combination = self.get_context_data(request, id, column)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s-%s.csv"' % (score.name, test)
        writer = csv.writer(response)
        data_source_class = TEST_DATA.get(test)
        data_source = data_source_class()
        writer.writerows(data_source.as_array(score, test, combination))
        return response


class TableCSVExportView(View):
    def parse_value(self, value):
        mapping = {YES:PASS, NO:FAIL, NOT_REPORTING:N_A}
        return mapping.get(value, value)

    def get(self, request):
        formulation = request.GET.get('formulation', F1)
        cycle = request.GET.get('cycle', None)
        columns = ScoresTableView.columns
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="facilitytable-%s-%s.csv"' % (cycle, formulation)
        writer = csv.writer(response)
        writer.writerow(columns)
        filter = {'cycle': cycle}
        if self.request.user:
            if self.request.user.access_level and self.request.user.access_area:
                filters[self.request.user.access_level.lower()] = self.request.user.access_area
        for score in Score.objects.filter(**filter).order_by('name'):
            row = []
            for c in columns:
                value = getattr(score, c)
                if type(value) is dict:
                    if DEFAULT in value:
                        row.append(self.parse_value(value.get(DEFAULT)))
                    else:
                        row.append(self.parse_value(value.get(formulation)))
                else:
                    row.append(value)
            writer.writerow(row)

        return response
