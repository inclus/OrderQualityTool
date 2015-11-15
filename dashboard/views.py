import os

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.generic import TemplateView, FormView

from forms import FileUploadForm


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"


class DataImportView(LoginRequiredMixin, FormView):
    template_name = "import.html"
    form_class = FileUploadForm

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        file_type = form.cleaned_data['file_type']
        path = default_storage.save('tmp/workspace.xlsx', ContentFile(import_file.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)

        return super(DataImportView, self).form_valid(form)
