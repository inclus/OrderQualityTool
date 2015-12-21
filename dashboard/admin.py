from admirarchy.utils import HierarchicalModelAdmin
from custom_user.forms import EmailUserChangeForm, EmailUserCreationForm
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext_lazy as _

from dashboard.models import DashboardUser, Consumption, Cycle, AdultPatientsRecord, PAEDPatientsRecord, CycleScore, CycleFormulationScore, Score
from dashboard.tasks import calculate_scores_for_checks_in_cycle
from locations.models import Facility, WareHouse, IP, District


class EmailUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((
                         None, {
                             'classes': ('wide',),
                             'fields': ('email', 'password1', 'password2')
                         }
                     ),
    )

    form = EmailUserChangeForm
    add_form = EmailUserCreationForm

    list_display = ('email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)


class QdbSite(AdminSite):
    site_title = ugettext_lazy('Order Quality admin')

    site_header = ugettext_lazy('Order Quality administration')

    index_title = ugettext_lazy('Order Quality administration')


class MyModelAdmin(HierarchicalModelAdmin):
    hierarchy = True


class ConsumptionAdmin(ModelAdmin):
    list_display = (
        'facility_cycle',
        'formulation',
        'opening_balance',
        'quantity_received',
        'pmtct_consumption',
        'art_consumption',
        'loses_adjustments',
        'closing_balance',
        'months_of_stock_of_hand',
        'quantity_required_for_current_patients',
        'estimated_number_of_new_patients',
        'estimated_number_of_new_pregnant_women'
    )


class PatientAdmin(ModelAdmin):
    list_display = ('facility_cycle',
                    'formulation',
                    'existing',
                    'new'
                    )


class FacilityAdmin(ModelAdmin):
    list_display = ('name',
                    'warehouse',
                    'ip',
                    'district'
                    )


def run_tests(model_admin, request, queryset):
    data = queryset.order_by().values('cycle').distinct()
    for value in data:
        calculate_scores_for_checks_in_cycle.delay(value['cycle'])


run_tests.short_description = "Run quality tests for these cycles"


class FacilityCycleRecordAdmin(ModelAdmin):
    list_display = ('facility',
                    'reporting_status',
                    'web_based',
                    'multiple',
                    'cycle'
                    )
    list_filter = ('reporting_status', 'multiple', 'cycle')
    actions = [run_tests]


class ScoreAdmin(ModelAdmin):
    list_display = ('name', 'cycle', 'formulation', 'district', 'ip', 'warehouse', 'nnrtiNewPaed',
                    'stablePatientVolumes',
                    'REPORTING',
                    'consumptionAndPatients',
                    'nnrtiCurrentPaed',
                    'warehouseFulfilment',
                    'differentOrdersOverTime',
                    'closingBalanceMatchesOpeningBalance',
                    'WEB_BASED',
                    'OrderFormFreeOfGaps',
                    'MULTIPLE_ORDERS',
                    'nnrtiNewAdults',
                    'orderFormFreeOfNegativeNumbers',
                    'nnrtiCurrentAdults',
                    'stableConsumption',
                    )
    list_filter = ('formulation', 'cycle')

    def cycle(self, obj):
        return obj.facility_cycle.cycle

    def facility(self, obj):
        return obj.facility_cycle.facility


admin_site = QdbSite()
admin_site.register(Group, GroupAdmin)
admin_site.register(DashboardUser, EmailUserAdmin)
admin_site.register(Facility, FacilityAdmin)
admin_site.register(IP)
admin_site.register(WareHouse)
admin_site.register(District)
admin_site.register(CycleScore)
admin_site.register(Score, ScoreAdmin)
admin_site.register(CycleFormulationScore)
admin_site.register(AdultPatientsRecord, PatientAdmin)
admin_site.register(PAEDPatientsRecord, PatientAdmin)
admin_site.register(Consumption, ConsumptionAdmin)
admin_site.register(Cycle, FacilityCycleRecordAdmin)
