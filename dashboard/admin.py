# Register your models here.
from admirarchy.utils import HierarchicalModelAdmin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy

from locations.models import Location


class QdbSite(AdminSite):
    site_title = ugettext_lazy('Order Quality Tool admin')

    site_header = ugettext_lazy('Order Quality Tool administration')

    index_title = ugettext_lazy('Order Quality Tool administration')


class MyModelAdmin(HierarchicalModelAdmin):
    hierarchy = True  # This enables hierarchy handling.


admin_site = QdbSite()
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Location, MyModelAdmin)
