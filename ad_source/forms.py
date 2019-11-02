from django.forms import ModelForm

from . import models


class TaskForm(ModelForm):
    class Meta:
        model = models.Task
        fields = [
            'website_link',
            'title',
            'description',
            'reward_per_click',
            'time_duration',

        ]
