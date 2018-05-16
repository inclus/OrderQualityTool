from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

import dashboard.views.api
import dashboard.views.main
import dashboard.views.tables
import dashboard.views.upload_users
import dashboard.views.definition


urlpatterns = [
    url(r"^$", dashboard.views.main.HomeView.as_view(), name="home"),
    url(r"^about/$", dashboard.views.main.AboutPageView.as_view(), name="about"),
    url(
        r"^about/tests$",
        dashboard.views.main.AboutTestPageView.as_view(),
        name="about.tests",
    ),
    url(
        r"^about/background$",
        dashboard.views.main.AboutBackground.as_view(),
        name="about.background",
    ),
    url(
        r"^about/how_works$",
        dashboard.views.main.AboutHowWorks.as_view(),
        name="about.how_works",
    ),
    url(
        r"^about/how_used$",
        dashboard.views.main.AboutHowUsed.as_view(),
        name="about.how_used",
    ),
    url(r"^import/$", dashboard.views.main.DataImportView.as_view(), name="import"),
    url(
        r"^import/dhis2$", dashboard.views.main.Dhis2ImportView.as_view(), name="import"
    ),
    url(
        r"^import/mapping/$",
        dashboard.views.main.PartnerMappingImportPage.as_view(),
        name="update_partner_mapping",
    ),
    url(
        r"^import/mapping/download/$",
        dashboard.views.main.download_mapping,
        name="download_partner_mapping",
    ),
    url(
        r"^import/users/$",
        dashboard.views.upload_users.UserImportView.as_view(),
        name="import_users",
    ),
    url(r"^reports/$", dashboard.views.main.ReportsView.as_view(), name="reports"),
    url(
        r"^api/test/(?P<id>\d+)/",
        dashboard.views.api.ScoresAPIView.as_view(),
        name="test_scores_api",
    ),
    url(
        r"^api/test/list/",
        dashboard.views.api.GetTestsAPIView.as_view(),
        name="featured_tests",
    ),
    url(
        r"^api/test/ranking/best$",
        dashboard.views.api.BestPerformingDistrictsView.as_view(),
        name="ranking_best",
    ),
    url(
        r"^api/test/ranking/worst$",
        dashboard.views.api.WorstPerformingDistrictsView.as_view(),
        name="ranking_worst",
    ),
    url(
        r"^api/test/ranking/best/csv$",
        dashboard.views.api.BestPerformingDistrictsCSVView.as_view(),
        name="ranking_best_csv",
    ),
    url(
        r"^api/test/ranking/worst/csv$",
        dashboard.views.api.WorstPerformingDistrictsCSVView.as_view(),
        name="ranking_worst_csv",
    ),
    url(r"^api/cycles$", dashboard.views.api.CyclesView.as_view(), name="cycles"),
    url(
        r"^api/formulations/adult",
        dashboard.views.api.ListAdultFormulations.as_view(),
        name="formulations_adult",
    ),
    url(
        r"^api/formulations/paed",
        dashboard.views.api.ListPaedFormulations.as_view(),
        name="formulations_paed",
    ),
    url(
        r"^api/formulations/consumption",
        dashboard.views.api.ListConsumptionFormulations.as_view(),
        name="formulations_consumption",
    ),
    url(
        r"^api/fields/consumption",
        dashboard.views.api.ListConsumptionFields.as_view(),
        name="consumption_fields",
    ),
    url(
        r"^api/fields/patients",
        dashboard.views.api.ListPatientFields.as_view(),
        name="patient_fields",
    ),
    url(
        r"^api/scores",
        dashboard.views.api.FacilityTestCycleScoresListView.as_view(),
        name="scores",
    ),
    url(
        r"^api/filters", dashboard.views.api.FilterValuesView.as_view(), name="filters"
    ),
    url(
        r"^api/rankingsAccess",
        dashboard.views.api.RankingsAccessView.as_view(),
        name="rankings-access",
    ),
    url(
        r"^api/table/scores$",
        csrf_exempt(dashboard.views.tables.ScoresTableView.as_view()),
        name="scores-table",
    ),
    url(
        r"^api/table/scores/detail/(?P<id>\d+)/(?P<column>\d+$)",
        csrf_exempt(dashboard.views.tables.ScoreDetailsView.as_view()),
        name="scores-detail",
    ),
    url(
        r"^api/table/scores/csv/(?P<id>\d+)/(?P<column>\d+$)",
        csrf_exempt(dashboard.views.tables.ScoreDetailsCSVView.as_view()),
        name="scores-detail-csv",
    ),
    url(
        r"^api/access/areas$",
        csrf_exempt(dashboard.views.api.AccessAreasView.as_view()),
        name="access-areas",
    ),
    url(
        r"^api/tables/export/csv$",
        dashboard.views.tables.TableCSVExportView.as_view(),
        name="export-table",
    ),
    url(
        r"^api/access/admin$",
        dashboard.views.api.AdminAccessView.as_view(),
        name="admin-view",
    ),
    url(
        r"^api/import/dhis2$",
        dashboard.views.api.NewImportView.as_view(),
        name="dhis2-import",
    ),
    url(
        r"^api/tests/preview$",
        dashboard.views.definition.PreviewDefinitionView.as_view(),
        name="preview-definition",
    ),
    url(
        r"^api/tests/preview/locations$",
        dashboard.views.definition.PreviewLocationsView.as_view(),
        name="preview-locations",
    ),
    url(
        r"^api/tests/tracingformulations",
        dashboard.views.definition.TracingFormulationView.as_view(),
        name="tracing-consumption",
    ),
    url(
        r"^api/test/metrics",
        dashboard.views.api.ReportMetrics.as_view(),
        name="metrics",
    ),
]
