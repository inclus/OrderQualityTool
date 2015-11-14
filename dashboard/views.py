from braces.views import LoginRequiredMixin
from django.views.generic import TemplateView, FormView
from forms import FileUploadForm

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

class DataImportView(LoginRequiredMixin, FormView):
    template_name = "import.html"
    form_class = FileUploadForm
