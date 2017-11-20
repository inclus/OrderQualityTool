from django.core.urlresolvers import reverse
from menu import Menu, MenuItem


def user_is_admin(request):
    return request.user and (request.user.is_staff or request.user.is_superuser)


def user_is_super_user(request):
    return request.user and request.user.is_superuser


Menu.add_item("main", MenuItem("DASHBOARD",
                               reverse("home"),
                               weight=10))

Menu.add_item("main", MenuItem("FACILITY REPORT",
                               reverse("reports"),
                               weight=10))

Menu.add_item("main", MenuItem("ABOUT",
                               reverse("about"),
                               weight=10))

Menu.add_item("main", MenuItem("TESTS",
                               reverse("about.tests"),
                               weight=10))

# Menu.add_item("main", MenuItem("IMPORT FILES",
#                                reverse("import"),
#                                check=user_is_admin,
#                                weight=20))
Menu.add_item("main", MenuItem("PARTNER MAPPING",
                               reverse("update_partner_mapping"),
                               check=user_is_admin,
                               weight=20))

Menu.add_item("main", MenuItem("USERS",
                               reverse("users"),
                               check=user_is_super_user,
                               weight=20))
