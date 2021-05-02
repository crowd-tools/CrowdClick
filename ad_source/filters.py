from django_filters import rest_framework as filters

from . import models

TASK_TYPE_QUIZ = 'quiz'
TASK_TYPE_CAMPAIGN = 'campaign'

TASK_TYPE_CHOICES = {
    (TASK_TYPE_QUIZ, TASK_TYPE_QUIZ),
    (TASK_TYPE_CAMPAIGN, TASK_TYPE_CAMPAIGN),
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
