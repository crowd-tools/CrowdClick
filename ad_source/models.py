import datetime
from decimal import Decimal as D

from django.core.cache import cache
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from . import managers
from .management.commands.fetch_eth_price import CACHE_KEY as FETCH_ETH_PRICE_CACHE_KEY


class Task(models.Model):
    title = models.CharField("Title", max_length=100)
    description = models.TextField("Description", max_length=100)
    website_link = models.URLField("Website Link")
    reward_per_click = models.DecimalField("Reward per click", max_digits=9, decimal_places=3)  # ETH but shown as USD
    image = models.ImageField("Image", upload_to="assets/task_image", default="placeholder.png")
    image_thumbnail = ImageSpecField(
        source='image', processors=[ResizeToFill(150, 150)], format='JPEG', options={'quality': 60}
    )

    spend_daily = models.DecimalField("Max budget to spend per day", max_digits=9, decimal_places=3)
    time_duration = models.DurationField("Time duration", default=datetime.timedelta(seconds=30))
    created = models.DateTimeField(auto_created=True)  # No show

    objects = managers.TaskManager()

    class Meta:
        ordering = ['-reward_per_click']

    @property
    def reward_usd_per_click(self):
        eth_to_usd = cache.get(FETCH_ETH_PRICE_CACHE_KEY)
        if eth_to_usd:
            return self.reward_per_click * D(str(eth_to_usd))


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
    result_count = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return "Question(%s, title=%s)" % (self.title, self.question_type)


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    result_count = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return "Answer(%s, title=%s)" % (self.pk, self.title)


class Subscribe(models.Model):
    email = models.EmailField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
