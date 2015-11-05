# Register your models here.
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext_lazy


class QdbSite(AdminSite):
    site_title = ugettext_lazy('Order Quality Tool admin')

    site_header = ugettext_lazy('Order Quality Tool administration')

    index_title = ugettext_lazy('Order Quality Tool administration')


admin_site = QdbSite()
admin_site.register(Group, GroupAdmin)
admin_site.register(User, UserAdmin)
