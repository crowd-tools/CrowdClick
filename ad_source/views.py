from django.http import HttpResponse
from django.views.generic.base import TemplateView


def landing_page(request):
    return HttpResponse("Hello, world. You're at the polls index.")


class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs


home = HomeView.as_view()
