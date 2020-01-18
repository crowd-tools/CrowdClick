from django.db import models
from django.db.models import Count


class TaskManager(models.Manager):
    def get_queryset(self):
        return super(TaskManager, self).get_queryset().prefetch_related('questions', 'questions__options')

    # TODO Manager property `spend_today` - moving window since time `created`

    def active(self, user):
        # XXX Extend SQL property `is_active` - we can spend from user account + didn't exceeded `spend_daily`
        filters = {}
        if not user.is_superuser:
            filters.update({"is_active": True})
        return self.get_queryset().filter(**filters)

    # Publisher

    def dashboard(self, user):
        return self.get_queryset().filter(user=user).annotate(
            answers_result_count=Count('answers')
        )
