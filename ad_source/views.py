from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.urls import reverse

from . import forms, models


class HomeView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs


class LogoutView(auth_views.LogoutView):
    pass


class AboutView(TemplateView):
    template_name = "home/about.html"


class PublishView(FormView):
    template_name = "home/publish.html"
    form_class = forms.AdvertisementForm
    success_url = "/advertisement"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        questions = models.Question.objects.all()
        kwargs["questions"] = questions
        return kwargs

    def form_valid(self, form):
        question = models.Question.objects.get(pk=form.data['question'])
        ad = form.save()
        question.ad = ad
        question.save()
        return super().form_valid(form)


class AdvertisementView(TemplateView):
    template_name = "home/advertisement.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["advertisements"] = models.Advertisement.objects.all()
        return kwargs


class EarnView(TemplateView):
    template_name = "home/earn.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["ad"] = models.Advertisement.objects.get(pk=kwargs.get("ad_id"))
        return kwargs

    def post(self, request, **kwargs):
        for key, value in request.POST.items():
            if key.startswith('question_'):
                _, q_id = key.split('_')
                question = models.Question.objects.get(pk=q_id)
                answer = models.Answer.objects.get(pk=value)
                print("Question: %s, Answer %s" % (question.id, answer.id))  # TODO store result to database?
        return HttpResponseRedirect((reverse('advertisement')))


home = HomeView.as_view()
about = AboutView.as_view()
publish = PublishView.as_view()
advertisement = AdvertisementView.as_view()
logout = LogoutView.as_view()
earn = EarnView.as_view()
