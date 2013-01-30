# Create your views here.
from django.views.generic.base import TemplateView


class DashboardView(TemplateView):
    
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        return None
