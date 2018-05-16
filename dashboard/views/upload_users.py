import csv
from io import StringIO

from braces.views import SuperuserRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.generic import FormView

from dashboard.forms import UserUploadForm
from dashboard.models import DashboardUser


def emailIsValid(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class UserImportView(LoginRequiredMixin, SuperuserRequiredMixin, FormView):
    template_name = "import.html"
    form_class = UserUploadForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super(UserImportView, self).get_context_data(**kwargs)
        context["title"] = "Upload Users"
        return context

    def form_valid(self, form):
        import_file = StringIO(form.cleaned_data["import_file"].read().decode())
        reader = csv.reader(import_file)
        for row in reader:
            email, password, role, access_area, superuser = row
            if emailIsValid(email):
                is_superuser = superuser == "YES"
                user, created = DashboardUser.objects.get_or_create(email=email)
                if created:
                    user.is_staff = is_superuser
                    user.is_superuser = is_superuser
                    user.access_level = role
                    user.access_area = access_area if access_area != "" else None
                    user.set_password(password)
                    user.save()
        return super(UserImportView, self).form_valid(form)
