from django.db import models
from django.db.models import Count


class TaskManager(models.Manager):
    def get_queryset(self):
        return super(TaskManager, self).get_queryset().prefetch_related(
            'questions', 'questions__options'
        ).order_by('-reward_per_click')

    # TODO Manager property `spend_today` - moving window since time `created`

    def active(self, user):
        # XXX Extend SQL property `is_active` - we can spend from user account + didn't exceeded `spend_daily`
        filters = {}
        filters.update({"is_active": True})
        qs = self.get_queryset().filter(**filters)
        if user.is_authenticated:
            qs = qs.exclude(
                # Exclude tasks that user already answered
                id__in=user.answers.values_list('task')
            )
        return qs

    def dashboard(self, user):
        return self.get_queryset().filter(user=user).annotate(
            answers_result_count=Count('answers')
        )


class OptionManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(answer_count=Count('answers'))
        return qs
