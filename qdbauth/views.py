from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from custom_user.forms import EmailUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.views.generic import ListView, FormView


class UserListView(LoginRequiredMixin, SuperuserRequiredMixin, ListView):
    model = get_user_model()


class NewUserForm(EmailUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'is_staff', 'is_superuser', 'access_level')


class EditUserForm(ModelForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'is_staff', 'is_superuser', 'access_level')


class UserAddView(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    template_name = "dashboard/dashboarduser_form.html"
    form_class = NewUserForm

    def get_context_data(self, **kwargs):
        data = super(UserAddView, self).get_context_data(**kwargs)
        data['page_header'] = "Create User"
        return data

    def get_success_url(self):
        return reverse("users")

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class UserEditView(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    template_name = "dashboard/dashboarduser_form.html"
    form_class = EditUserForm

    def get_context_data(self, **kwargs):
        data = super(UserEditView, self).get_context_data(**kwargs)
        data['page_header'] = "Edit User"
        return data

    def get_form(self, form_class=None):
        user = get_user_model().objects.get(pk=(self.kwargs.get('pk')))
        return self.form_class(instance=user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse("users")

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())


class ChangePasswordView(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    template_name = "dashboard/dashboarduser_form.html"
    form_class = AdminPasswordChangeForm

    def get_context_data(self, **kwargs):
        data = super(ChangePasswordView, self).get_context_data(**kwargs)
        data['page_header'] = "Change Password"
        return data

    def get_form(self, form_class=None):
        user = get_user_model().objects.get(pk=(self.kwargs.get('pk')))
        return self.form_class(user, **self.get_form_kwargs())

    def get_success_url(self):
        return reverse("users")

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())
