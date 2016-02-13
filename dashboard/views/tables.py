import pydash
from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView
from rest_framework.response import Response
from rest_framework.views import APIView

from dashboard.data.consumption_patients import ConsumptionAndPatientsQualityCheck
from dashboard.data.negatives import NegativeNumbersQualityCheck
from dashboard.helpers import *
from dashboard.models import Score, Consumption, PAEDPatientsRecord, AdultPatientsRecord


class ScoresTableView(BaseDatatableView):
    model = Score
    columns = [
        NAME,
        DISTRICT.lower(),
        WAREHOUSE.lower(),
        IP.lower(),
        REPORTING,
        WEB_BASED,
        MULTIPLE_ORDERS,
        ORDER_FORM_FREE_OF_GAPS,
        GUIDELINE_ADHERENCE_ADULT_1L,
        GUIDELINE_ADHERENCE_ADULT_2L,
        GUIDELINE_ADHERENCE_PAED_1L,
        NNRTI_NEW_PAED,
        NNRTI_CURRENT_PAED,
        NNRTI_NEW_ADULTS,
        NNRTI_CURRENT_ADULTS,
        STABLE_PATIENT_VOLUMES,
        CONSUMPTION_AND_PATIENTS,
        WAREHOUSE_FULFILMENT,
        DIFFERENT_ORDERS_OVER_TIME,
        CLOSING_BALANCE_MATCHES_OPENING_BALANCE,
        ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS,
        STABLE_CONSUMPTION,
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
                           WEB_BASED,
                           MULTIPLE_ORDERS,
                           ORDER_FORM_FREE_OF_GAPS,
                           GUIDELINE_ADHERENCE_ADULT_1L,
                           GUIDELINE_ADHERENCE_ADULT_2L,
                           GUIDELINE_ADHERENCE_PAED_1L,
                           NNRTI_NEW_PAED,
                           NNRTI_CURRENT_PAED,
                           NNRTI_NEW_ADULTS,
                           NNRTI_CURRENT_ADULTS, ]
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


query_map = {F1: F1_QUERY, F2: F2_QUERY, F3: F3_QUERY}

class CheckDataSource():
    def load(self):
	pass

class NegativesCheckDataSource(CheckDataSource):
    def load(self, score, test, combination):
    	return self.get_negatives_data(score, test, combination)

    def get_negatives_data(self, score, test, combination):
        check = NegativeNumbersQualityCheck({})
        formulation_query = query_map.get(combination)
        consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__icontains=formulation_query)
        tables = []
        for consumption in consumption_records:
            formulation_data = {"name": consumption.formulation}
            records = []
            for field in check.fields:
                records.append({"column": FIELD_NAMES.get(field), "value": getattr(consumption, field)})
            formulation_data['records'] = records
            tables.append(formulation_data)
        return {"main_title": "RAW ORDER DATA", "template": "#%s" % test, "formulations": tables}

class ConsumptionAndPatientsDataSource(CheckDataSource):
    def load(self, score, test, combination):
        return self.get_consumption_and_patients(score, test, combination)

    def get_consumption_and_patients(self, score, test, combination_name):
        check = ConsumptionAndPatientsQualityCheck({})
        check_combination = get_combination(check.combinations, combination_name)
        formulation_query = check_combination.get(CONSUMPTION_QUERY)
        consumption_records = Consumption.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__icontains=formulation_query)
        tables = []
        for consumption in consumption_records:
            formulation_data = {"name": consumption.formulation}
            records = []
            sum = 0
            for field in check_combination.get(FIELDS, []):
                value = getattr(consumption, field)
                sum += value
                records.append({"column": FIELD_NAMES.get(field), "value": value})
            records.append({"column": "Total", "value": sum})

            formulation_data['records'] = records
            tables.append(formulation_data)
        model = AdultPatientsRecord if check_combination.get(IS_ADULT, False) else PAEDPatientsRecord
        patient_records = model.objects.filter(name=score.name, district=score.district, cycle=score.cycle, formulation__in=check_combination.get(PATIENT_QUERY))
        patient_tables = []
        for pr in patient_records:
            formulation_data = {"name": pr.formulation}
            records = []
            sum = 0
            for field in [NEW, EXISTING]:
                value = getattr(pr, field)
                sum += value
                records.append({"column": FIELD_NAMES.get(field), "value": value})
            records.append({"column": "Total", "value": sum})
            formulation_data['records'] = records
            patient_tables.append(formulation_data)
        return {"main_title": "RAW ORDER DATA", "template": "#%s" % test, "consumption": tables, "patients": patient_tables}

def get_combination(combinations, name):
    return pydash.select(combinations, lambda x: x[NAME] == name)[0]


class ScoreDetailsView(APIView):
    def get(self, request, id, column):
        TEST_DATA = {
            ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS: NegativesCheckDataSource,
            CONSUMPTION_AND_PATIENTS: ConsumptionAndPatientsDataSource
        }
        scores = {YES: "Pass", NO: "Fail", NOT_REPORTING: "N/A"}
        combination = request.GET.get('combination', DEFAULT)
        column = int(column)
        score = Score.objects.get(id=id)
        score_data = {'ip': score.ip, 'district': score.district, 'warehouse': score.warehouse, 'name': score.name, 'cycle': score.cycle}
        has_result = column > 3
        response_data = {'score': score_data, 'has_result': has_result}
        if has_result:
            view = ScoresTableView()
            test = view.columns[column]
            if test in TEST_DATA:
                data_source_class = TEST_DATA.get(test)
                data_source = data_source_class()
                response_data['data'] = data_source.load(score, test, combination)
            result = getattr(score, test, None)

            def combination_yes():
                return result.get(combination) if type(result) == dict else result

            def combination_no():
                return result.get(DEFAULT, None) if type(result) == dict else result

            actual_result = combination_yes() if combination in result else combination_no
            result_data = {'test': TEST_NAMES.get(test, None), 'result': scores.get(actual_result), 'has_combination': len(result) > 1}
            response_data['result'] = result_data
        return Response(response_data)
