from django.db import models


class TaskManager(models.Manager):
    def get_queryset(self):
        return super(TaskManager, self).get_queryset().prefetch_related('questions', 'questions__answers')

    # TODO SQL property `spend_today` - moving window since time `created`
    # TODO SQL property `is_active` - we can spend from user account + didn't exceeded `spend_daily`
