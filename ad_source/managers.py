from django.db import models
from django.db.models import Count


class TaskManager(models.Manager):
    def get_queryset(self):
        return super(TaskManager, self).get_queryset().prefetch_related(
            'questions', 'questions__options'
        ).order_by('-reward_per_click')

    def active_for_user(self, user):
        # Filter for active tasks
        filters = {"is_active": True, "is_active_web3": True}
        qs = self.get_queryset().filter(**filters)
        # Filter for tasks having `remaining balance` >= `reward per click` OR `remaining balance` IS NULL
        qs = qs.filter(
            models.Q(remaining_balance__gte=models.F('reward_per_click')) | models.Q(remaining_balance__isnull=True)
        )
        if user.is_authenticated:
            # Exclude tasks that user already answered
            qs = qs.exclude(
                id__in=user.answers.values_list('task')
            )
        return qs

    def dashboard(self, user):
        return self.get_queryset().filter(user=user).annotate(
            answers_result_count=Count('answers')
        )


class QuestionManager(models.Manager):
    def get_queryset(self):
        qs = super(QuestionManager, self).get_queryset()
        qs = qs.annotate(
            is_quiz=models.Case(
                models.When(options__is_correct=True, then=True),
                default=False,
                output_field=models.BooleanField(),
            ),
        )
        return qs


class OptionManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(answer_count=Count('answers'))
        return qs
