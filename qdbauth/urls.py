from django.conf.urls import url
from django.contrib.auth.views import login, logout

from qdbauth.views import UserListView, UserAddView

urlpatterns = [
    url(r'^login$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout$', logout, {'template_name': 'logout.html'}, name='logout'),
    url(r'^users$', UserListView.as_view(), name='users'),
    url(r'^users/add$', UserAddView.as_view(), name='users-add')
]
