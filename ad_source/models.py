from django.db import models
import datetime

from . import managers


class Task(models.Model):
    website_link = models.URLField("Website Link")
    title = models.CharField("Title", max_length=35)
    description = models.TextField("Description", max_length=100, null=True, blank=True)
    reward_per_click = models.FloatField("Reward per click", default=1)
    time_duration = models.DurationField("Time duration", default=datetime.timedelta(seconds=30))

    objects = managers.TaskManager()

    class Meta:
        ordering = ['-reward_per_click']


class Question(models.Model):
    RADIO_TYPE = 'RA'
    SELECT_TYPE = 'SE'
    QUESTION_TYPES = (
        (RADIO_TYPE, 'Radio'),
        (SELECT_TYPE, 'Select'),
    )

    task = models.ForeignKey(Task, related_name="questions", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)

    def __str__(self):
        return "Question(%s, title=%s)" % (self.title, self.question_type)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)

    def __str__(self):
        return "Answer(%s, title=%s)" % (self.pk, self.title)
