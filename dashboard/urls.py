from django.conf.urls import url

from dashboard import views

urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^import/$', views.DataImportView.as_view(), name='import'),
    url(r'^api/cycleRecords$', views.CycleRecordsListView.as_view(), name='list_cycle_records'),
    url(r'^api/drugFormations', views.DrugFormulationListView.as_view(), name='list_drug_formations'),
    url(r'^api/consumptionRecords', views.ConsumptionRecordListView.as_view(), name='list_consumption_record'),
    url(r'^api/test/reportingRate', views.FacilitiesReportingView.as_view(), name='reporting_rate')
]
