from django.db.models import Q
from django_datatables_view.base_datatable_view import BaseDatatableView

from dashboard.helpers import F1, NOT_REPORTING, NO, YES
from dashboard.models import Score

DEFAULT = 'DEFAULT'

DEFAULT = 'DEFAULT'


class ScoresTableView(BaseDatatableView):
    model = Score
    columns = [
        'name',
        'district',
        'warehouse',
        'ip',
        'REPORTING',
        'WEB_BASED',
        'MULTIPLE_ORDERS',
        'OrderFormFreeOfGaps',
        'guidelineAdherenceAdult1L',
        'guidelineAdherenceAdult2L',
        'guidelineAdherencePaed1L',
        'nnrtiNewPaed',
        'nnrtiCurrentPaed',
        'nnrtiNewAdults',
        'nnrtiCurrentAdults',
        'stablePatientVolumes',
        'consumptionAndPatients',
        'warehouseFulfilment',
        'differentOrdersOverTime',
        'closingBalanceMatchesOpeningBalance',
        'orderFormFreeOfNegativeNumbers',
        'stableConsumption',
    ]
    order_columns = columns

    def render_column(self, row, column):
        display_text = {YES: 'PASS', NO: 'FAIL', NOT_REPORTING: 'N/A'}
        default_columns = ['REPORTING', 'WEB_BASED', 'MULTIPLE_ORDERS', 'OrderFormFreeOfGaps', 'guidelineAdherenceAdult1L', 'guidelineAdherenceAdult2L', 'guidelineAdherencePaed1L', 'nnrtiNewPaed', 'nnrtiCurrentPaed',
                           'nnrtiNewAdults',
                           'nnrtiCurrentAdults', ]
        formulation_columns = ['stablePatientVolumes', 'consumptionAndPatients', 'warehouseFulfilment', 'differentOrdersOverTime', 'closingBalanceMatchesOpeningBalance', 'orderFormFreeOfNegativeNumbers', 'stableConsumption', ]
        formulation = self.request.POST.get(u'formulation', F1)
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
        district = self.request.POST.get(u'district', None)
        ip = self.request.POST.get(u'ip', None)
        warehouse = self.request.POST.get(u'warehouse', None)
        filters = {}
        if cycle:
            filters['cycle'] = cycle
        if district:
            filters['district'] = district
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
