from menu import Menu, MenuItem
from django.core.urlresolvers import reverse

def user_is_staff(request):
    return request.user and request.user.is_staff

Menu.add_item("main", MenuItem("DASHBOARD",
                               reverse("home"),
                               weight=10))

Menu.add_item("main", MenuItem("IMPORT FILES",
                               reverse("import"),
                               check=user_is_staff,
                               weight=20))
