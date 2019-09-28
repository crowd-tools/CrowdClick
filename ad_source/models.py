from django.db import models


# Create your models here.
class Advertisement(models.Model):
    website_link = models.URLField("Website Link")
    title = models.CharField("Title", max_length=35)
    description = models.TextField("Description", max_length=100)
    reward_per_click = models.FloatField("Reward per click")
    time_duration = models.DurationField("Time duration")


class Question(models.Model):
    RADIO_TYPE = 'RA'
    SELECT_TYPE = 'SE'
    QUESTION_TYPES = (
        (RADIO_TYPE, 'Radio'),
        (SELECT_TYPE, 'Select'),
    )

    ad = models.ForeignKey("Advertisement", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES)


class Answer(models.Model):
    question = models.ForeignKey("Question", on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
