from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView

from dashboard.helpers import *
from dashboard.helpers import FAIL_COUNT
from dashboard.models import Score


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
