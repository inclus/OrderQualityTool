import os

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.generic import TemplateView, FormView

from dashboard.models import WaosFile
from forms import FileUploadForm


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"


class DataImportView(LoginRequiredMixin, FormView):
    template_name = "import.html"
    form_class = FileUploadForm
    success_url = '/'

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        path = default_storage.save('tmp/workspace.xlsx', ContentFile(import_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        record = WaosFile(tmp_file).get_data()
        if record:
            messages.add_message(self.request, messages.INFO, 'Successfully imported file for %s for cycle %s' % (record.facility, record.cycle))
        os.remove(tmp_file)
        return super(DataImportView, self).form_valid(form)
