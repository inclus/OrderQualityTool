import os

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.generic import TemplateView, FormView

from dashboard.forms import FileUploadForm
from dashboard.tasks import import_general_report


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


class DataImportView(LoginRequiredMixin, StaffuserRequiredMixin, FormView):
    template_name = "import.html"
    form_class = FileUploadForm
    success_url = '/'

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        cycle = form.cleaned_data['cycle']
        path = default_storage.save('tmp/workspace.xlsx', ContentFile(import_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        import_general_report.delay(tmp_file, cycle)
        messages.add_message(self.request, messages.INFO, 'Successfully started import for cycle %s' % (cycle))
        return super(DataImportView, self).form_valid(form)


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "reports.html"