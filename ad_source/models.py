from django.db import models
from . import managers


class Advertisement(models.Model):
    website_link = models.URLField("Website Link")
    title = models.CharField("Title", max_length=35)
    description = models.TextField("Description", max_length=100)
    reward_per_click = models.FloatField("Reward per click")
    time_duration = models.DurationField("Time duration")

    objects = managers.AdvertisementManager()


class Question(models.Model):
    RADIO_TYPE = 'RA'
    SELECT_TYPE = 'SE'
    QUESTION_TYPES = (
        (RADIO_TYPE, 'Radio'),
        (SELECT_TYPE, 'Select'),
    )

    ad = models.ForeignKey(Advertisement, related_name="questions", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)

    def __str__(self):
        return "title='%s', question_type='%s'" % (self.title, self.question_type)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)

    def __str__(self):
        return "id='%s', title='%s'" % (self.pk, self.title)
