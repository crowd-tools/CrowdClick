from django.http import HttpResponse
from django.views.generic.base import TemplateView


class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs


class AboutView(TemplateView):
    template_name = "home/about.html"


home = HomeView.as_view()
about = AboutView.as_view()
