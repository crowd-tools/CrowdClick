from django_filters import rest_framework as filters

from . import models


class TaskFilter(filters.FilterSet):
    public_key = filters.CharFilter(field_name='user__username')

    class Meta:
        model = models.Task
        fields = ('chain', )
