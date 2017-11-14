from functools import cmp_to_key
from io import BytesIO

from braces.views import LoginRequiredMixin, StaffuserRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, FormView

from dashboard.data.data_import import ExcelDataImport
from dashboard.data.utils import timeit
from dashboard.forms import FileUploadForm
from dashboard.helpers import F3, F2, F1, sort_cycle
from dashboard.models import Score
from dashboard.tasks import update_checks


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


class AboutPageView(TemplateView):
    template_name = "about.html"


class AboutTestPageView(TemplateView):
    template_name = "about_tests.html"


class AboutBackground(TemplateView):
    template_name = "about_background.html"


class AboutHowWorks(TemplateView):
    template_name = "about_works.html"


class AboutHowUsed(TemplateView):
    template_name = "about_used.html"


class DataImportView(LoginRequiredMixin, StaffuserRequiredMixin, FormView):
    template_name = "import.html"
    form_class = FileUploadForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super(DataImportView, self).get_context_data(**kwargs)
        context['title'] = "Upload New Cycle"
        return context

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        cycle = form.cleaned_data['cycle']
        report = parse_excel_file(cycle, import_file)
        cycle = save_data_import(report)
        update_checks.apply_async(args=[[cycle.id]], priority=1)
        messages.add_message(self.request, messages.INFO, 'Successfully started import for cycle %s' % (cycle))
        return super(DataImportView, self).form_valid(form)


@timeit
def parse_excel_file(cycle, excel_file):
    report = ExcelDataImport(BytesIO(excel_file.read()), cycle).load()
    return report


@timeit
def save_data_import(report):
    return report.save()


DEFAULT = 'DEFAULT'


class ReportsView(LoginRequiredMixin, TemplateView):
    template_name = "scores_table.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ReportsView, self).get_context_data(*args, **kwargs)
        access_level = self.request.user.access_level
        access_area = self.request.user.access_area
        qs_filter = {}
        if access_level and access_area:
            qs_filter[access_level.lower()] = access_area
        qs = Score.objects.filter(**qs_filter)
        ips = qs.values('ip').order_by('ip').distinct()
        warehouses = qs.values('warehouse').order_by('warehouse').distinct()
        districts = qs.values('district').order_by('district').distinct()
        raw_cycles = [c[0] for c in qs.values_list('cycle').distinct()]
        cycles = sorted(raw_cycles, key=cmp_to_key(sort_cycle), reverse=True)
        context['districts'] = districts
        context['ips'] = ips
        context['warehouses'] = warehouses
        context['cycles'] = cycles
        context['formulations'] = [F1, F2, F3]
        return context
