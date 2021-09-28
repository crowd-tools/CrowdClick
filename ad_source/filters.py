from django.db.models import Q, F
from django_filters import rest_framework as filters

from . import models

TASK_TYPE_QUIZ = 'quiz'
TASK_TYPE_CAMPAIGN = 'campaign'

TASK_TYPE_CHOICES = {
    (TASK_TYPE_QUIZ, TASK_TYPE_QUIZ),
    (TASK_TYPE_CAMPAIGN, TASK_TYPE_CAMPAIGN),
}

TASK_STATUS_ACTIVE = 'active'
TASK_STATUS_PAST = 'past'

TASK_STATUS_CHOICES = {
    (TASK_STATUS_ACTIVE, TASK_STATUS_ACTIVE),
    (TASK_STATUS_PAST, TASK_STATUS_PAST),
}


class TaskFilter(filters.FilterSet):
    public_key = filters.CharFilter(field_name='user__username')
    contract_address = filters.CharFilter(field_name='contract_address')
    type = filters.ChoiceFilter(
        method='filter_type',
        choices=TASK_TYPE_CHOICES,
        help_text=f"Options: {', '.join([k for k, v in TASK_TYPE_CHOICES])}"
    )

    class Meta:
        model = models.Task
        fields = ('chain',)

    def filter_type(self, queryset, name, value):
        if value == TASK_TYPE_QUIZ:
            queryset = queryset.filter(questions__options__is_correct=True)
        elif value == TASK_TYPE_CAMPAIGN:
            queryset = queryset.exclude(questions__options__is_correct=True)
        return queryset


class TaskDashboardFilter(TaskFilter):
    status = filters.ChoiceFilter(
        method='filter_status',
        choices=TASK_STATUS_CHOICES,
        help_text=f"Options: {', '.join([k for k, v in TASK_STATUS_CHOICES])}"
    )

    class Meta:
        model = models.Task
        fields = ('chain', 'is_private')

    def filter_status(self, queryset, name, value):
        if value == TASK_STATUS_ACTIVE:
            # Filter for active tasks
            queryset = queryset.filter(
                is_active_web3=True,
            )
            # Filter for tasks having `remaining balance` >= `reward per click` OR `remaining balance` IS NULL
            queryset = queryset.filter(
                Q(remaining_balance__gte=F('reward_per_click')) | Q(remaining_balance__isnull=True)
            )
        elif value == TASK_STATUS_PAST:
            # Filter for tasks having `remaining balance` < `reward per click` AND `remaining balance` IS NOT NULL
            queryset = queryset.filter(
                Q(is_active_web3=False) |
                (Q(remaining_balance__lt=F('reward_per_click')) &
                 Q(remaining_balance__isnull=False))
            )
        return queryset
