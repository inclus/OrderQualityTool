from django.conf.urls import url

from dashboard import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^import/$', views.DataImportView.as_view(), name='import'),
    url(r'^api/cycleRecords$', views.CycleRecordsListView.as_view(), name='list_cycle_records'),
    url(r'^api/consumptionRecords$', views.ConsumptionRecordListView.as_view(), name='list_consumption_record'),
    url(r'^api/test/submittedOrder', views.FacilitiesReportingView.as_view(), name='submiited_order'),
    url(r'^api/test/orderType', views.WebBasedReportingView.as_view(), name='order_type'),
    url(r'^api/test/facilitiesMultiple', views.FacilitiesMultipleReportingView.as_view(), name='facilities_multiple'),
    url(r'^api/test/orderFormFreeOfGaps', views.OrderFormFreeOfGapsView.as_view(), name='order_form_free_of_gaps'),
    url(r'^api/test/closingBalance', views.ClosingBalanceView.as_view(), name='closing_balance_matches_opening_balance'),
    url(r'^api/test/orderFormFreeOfNegativeNumbers', views.OrderFormFreeOfNegativeNumbersView.as_view(), name='order_form_free_of_negative_numbers'),
    url(r'^api/test/differentOrdersOverTime', views.DifferentOrdersOverTimeView.as_view(), name='different_orders_over_time'),
    url(r'^api/test/consumptionAndPatients', views.ConsumptionAndPatientsView.as_view(), name='consumption_and_patients'),
    url(r'^api/test/stableConsumption', views.StableConsumptionView.as_view(), name='stable_consumption'),
    url(r'^api/test/ranking/best', views.BestPerformingDistrictsView.as_view(), name='ranking_best'),
    url(r'^api/test/ranking/worst', views.WorstPerformingDistrictsView.as_view(), name='ranking_worst'),
    url(r'^api/test/ranking/best/csv$', views.BestPerformingDistrictsCSVView.as_view(), name='ranking_best_csv'),
    url(r'^api/test/ranking/worst/csv$', views.WorstPerformingDistrictsCSVView.as_view(), name='ranking_worst_csv'),
    url(r'^api/cycles$', views.CyclesView.as_view(), name='cycles'),
    url(r'^api/test/metrics', views.ReportMetrics.as_view(), name='metrics'),
    url(r'^api/regimens', views.RegimensListView.as_view(), name='regimens')
]
