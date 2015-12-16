from django.conf.urls import url

from dashboard import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^import/$', views.DataImportView.as_view(), name='import'),
    url(r'^reports/$', views.ReportsView.as_view(), name='reports'),
    url(r'^api/test/submittedOrder', views.FacilitiesReportingView.as_view(), name='submiited_order'),
    url(r'^api/test/orderType', views.WebBasedReportingView.as_view(), name='order_type'),
    url(r'^api/test/facilitiesMultiple', views.FacilitiesMultipleReportingView.as_view(), name='facilities_multiple'),
    url(r'^api/test/orderFormFreeOfGaps', views.OrderFormFreeOfGapsView.as_view(), name='order_form_free_of_gaps'),
    url(r'^api/test/closingBalance', views.ClosingBalanceView.as_view(), name='closing_balance_matches_opening_balance'),
    url(r'^api/test/orderFormFreeOfNegativeNumbers', views.OrderFormFreeOfNegativeNumbersView.as_view(), name='order_form_free_of_negative_numbers'),
    url(r'^api/test/differentOrdersOverTime', views.DifferentOrdersOverTimeView.as_view(), name='different_orders_over_time'),
    url(r'^api/test/consumptionAndPatients', views.ConsumptionAndPatientsView.as_view(), name='consumption_and_patients'),
    url(r'^api/test/stableConsumption', views.StableConsumptionView.as_view(), name='stable_consumption'),
    url(r'^api/test/stablePatientVolumes', views.StablePatientVolumesView.as_view(), name='stable_patient_volumes'),
    url(r'^api/test/warehouseFulfilment', views.WarehouseFulfilmentView.as_view(), name='warehouse_fulfilment'),
    url(r'^api/test/guidelineAdherence', views.GuideLineAdherenceView.as_view(), name='guideline_adherence'),
    url(r'^api/test/nnrtiCurrentAdults', views.NNRTICurrentAdultsView.as_view(), name='nnrti_current_adults'),
    url(r'^api/test/nnrtiCurrentPaed', views.NNRTICurrentPaedView.as_view(), name='nnrti_current_paed'),
    url(r'^api/test/nnrtiNewAdults', views.NNRTINewAdultsView.as_view(), name='nnrti_new_adults'),
    url(r'^api/test/nnrtiNewPaed', views.NNRTINewPaedView.as_view(), name='nnrti_new_paed'),
    url(r'^api/test/ranking/best', views.BestPerformingDistrictsView.as_view(), name='ranking_best'),
    url(r'^api/test/ranking/worst', views.WorstPerformingDistrictsView.as_view(), name='ranking_worst'),
    url(r'^api/test/ranking/best/csv$', views.BestPerformingDistrictsCSVView.as_view(), name='ranking_best_csv'),
    url(r'^api/test/ranking/worst/csv$', views.WorstPerformingDistrictsCSVView.as_view(), name='ranking_worst_csv'),
    url(r'^api/cycles$', views.CyclesView.as_view(), name='cycles'),
    url(r'^api/test/metrics', views.ReportMetrics.as_view(), name='metrics'),
    url(r'^api/regimens', views.RegimensListView.as_view(), name='regimens'),
    url(r'^api/scores', views.FacilityTestCycleScoresListView.as_view(), name='scores'),
    url(r'^api/filters', views.FilterValuesView.as_view(), name='filters'),
]
