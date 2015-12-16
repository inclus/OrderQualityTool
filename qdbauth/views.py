from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from custom_user.forms import EmailUserCreationForm
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, FormView

from dashboard.models import DashboardUser


class UserListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    model = DashboardUser


class UserForm(EmailUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'is_staff', 'is_superuser')


class UserAddView(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    template_name = "dashboard/dashboarduser_form.html"
    form_class = UserForm

    def get_success_url(self):
        return reverse("users")

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
