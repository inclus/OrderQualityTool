from admirarchy.utils import HierarchicalModelAdmin
from custom_user.forms import EmailUserChangeForm, EmailUserCreationForm
from django.contrib.admin import AdminSite, ModelAdmin
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy
from django.utils.translation import ugettext_lazy as _

from dashboard.models import DashboardUser, FacilityConsumptionRecord, DrugFormulation, FacilityCycleRecord
from locations.models import Location


class EmailUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password', 'location')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = ((
                         None, {
                             'classes': ('wide',),
                             'fields': ('email', 'password1', 'password2', 'location')
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
    list_display = ('facility_cycle',
                    'drug_formulation',
                    'opening_balance',
                    'quantity_received',
                    'pmtct_consumption',
                    'art_consumption',
                    'loses_adjustments',
                    'closing_balance',
                    'months_of_stock_of_hand',
                    'quantity_required_for_current_patients',
                    'estimated_number_of_new_patients',
                    'estimated_number_of_new_pregnant_women',
                    'total_quantity_to_be_ordered',
                    )


admin_site = QdbSite()
admin_site.register(Group, GroupAdmin)
admin_site.register(DashboardUser, EmailUserAdmin)
admin_site.register(Location, MyModelAdmin)
admin_site.register(FacilityConsumptionRecord, ConsumptionAdmin)
admin_site.register(DrugFormulation)
admin_site.register(FacilityCycleRecord)
