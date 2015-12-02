from django.conf.urls import url

from dashboard import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^import/$', views.DataImportView.as_view(), name='import'),
    url(r'^api/cycleRecords$', views.CycleRecordsListView.as_view(), name='list_cycle_records'),
    url(r'^api/consumptionRecords$', views.ConsumptionRecordListView.as_view(), name='list_consumption_record'),
    url(r'^api/test/reportingRate$', views.FacilitiesReportingView.as_view(), name='reporting_rate'),
    url(r'^api/test/webBased$', views.WebBasedReportingView.as_view(), name='web_based'),
    url(r'^api/test/reportingRate/bestDistricts$', views.BestPerformingDistrictsView.as_view(), name='reporting_rate_best'),
    url(r'^api/test/reportingRate/worstDistricts$', views.WorstPerformingDistrictsView.as_view(), name='reporting_rate_worst'),
     url(r'^api/test/reportingRate/best/csv$', views.BestPerformingDistrictsCSVView.as_view(), name='reporting_rate_best_csv'),
    url(r'^api/test/reportingRate/worst/csv$', views.WorstPerformingDistrictsCSVView.as_view(), name='reporting_rate_worst_csv'),
    url(r'^api/cycles$', views.CyclesView.as_view(), name='cycles'),
    url(r'^api/test/metrics', views.ReportMetrics.as_view(), name='metrics')
]
