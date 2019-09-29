from django.views.generic import FormView
from django.views.generic.base import TemplateView

from . import forms, models

class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs


class AboutView(TemplateView):
    template_name = "home/about.html"


class PublishView(FormView):
    template_name = "home/publish.html"
    form_class = forms.AdvertisementForm
    success_url = "."

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        questions = models.Question.objects.all()
        kwargs["questions"] = questions
        return kwargs


home = HomeView.as_view()
about = AboutView.as_view()
publish = PublishView.as_view()
