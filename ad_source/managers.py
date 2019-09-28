from django.db import models


class AdvertisementManager(models.Manager):
    def get_queryset(self):
        return super(AdvertisementManager, self).get_queryset().prefetch_related('questions', 'questions__answers')

