import datetime
from decimal import Decimal as D

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils import timezone

from . import managers
from .management.commands.fetch_eth_price import CACHE_KEY as FETCH_ETH_PRICE_CACHE_KEY
from .open_graph import OpenGraph


class Task(models.Model):
    title = models.CharField("Title", max_length=100)
    description = models.TextField("Description", max_length=100)
    website_link = models.URLField("Website Link")
    reward_per_click = models.DecimalField("Reward per click", max_digits=9, decimal_places=3)  # ETH but shown as USD
    og_image_link = models.URLField("OpenGraph Image Path", max_length=200, blank=True, null=True)
    spend_daily = models.DecimalField("Max budget to spend per day", max_digits=9, decimal_places=3)
    time_duration = models.DurationField("Time duration", default=datetime.timedelta(seconds=30))
    created = models.DateTimeField(default=timezone.now)  # No show
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='tasks', on_delete=models.DO_NOTHING)

    objects = managers.TaskManager()

    class Meta:
        ordering = ['-reward_per_click']

    @property
    def reward_usd_per_click(self):
        eth_to_usd = cache.get(FETCH_ETH_PRICE_CACHE_KEY)
        if eth_to_usd:
            return self.reward_per_click * D(str(eth_to_usd))

    def save(self, **kwargs):
        if not self.og_image_link:
            # Setup Open Graph Image if needed
            og = OpenGraph(url=self.website_link)
            self.og_image_link = og.image
        super().save(kwargs)


class Question(models.Model):
    RADIO_TYPE = 'RA'
    SELECT_TYPE = 'SE'
    QUESTION_TYPES = (
        (RADIO_TYPE, 'Radio'),
        (SELECT_TYPE, 'Select'),
    )

    task = models.ForeignKey(Task, related_name="questions", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default=SELECT_TYPE)

    def __str__(self):
        return "Question(%s, title=%s)" % (self.title, self.question_type)


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    def __str__(self):
        return "Option(%s, title=%s)" % (self.pk, self.title)


class SelectedOption(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE)


class AnsweredQuestion(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ManyToManyField(SelectedOption, related_name='answered_questions')


class Answer(models.Model):
    task = models.ForeignKey(Task, related_name='answers', on_delete=models.CASCADE)
    answered_questions = models.ManyToManyField(AnsweredQuestion, related_name='answers')
    user = models.ForeignKey(User, related_name='answers', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)


class Subscribe(models.Model):
    email = models.EmailField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
