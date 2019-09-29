from django.forms import ModelForm

from . import models


class AdvertisementForm(ModelForm):
    class Meta:
        model = models.Advertisement
        fields = [
            'website_link',
            'title',
            'description',
            'reward_per_click',
            'time_duration',

        ]