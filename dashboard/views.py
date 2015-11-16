import os

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Count
from django.views.generic import TemplateView, FormView

from dashboard.models import WaosFile, FacilityCycleRecord
from forms import FileUploadForm
from locations.models import Location


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        cycles = FacilityCycleRecord.objects.values('cycle').annotate(count=Count('facility'))
        locations_at_level_5 = Location.objects.filter(level=5).count()
        context['cycles'] = cycles
        context['location_count'] = locations_at_level_5
        return context


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
