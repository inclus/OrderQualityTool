from django.conf.urls import include, url

from dashboard import urls as dashboard_urls
from qdbauth import urls as auth_urls

urlpatterns = [
    url(r'^', include(dashboard_urls)),
    url(r'^', include(auth_urls)),
    url(r'^', include('password_reset.urls'))
]
