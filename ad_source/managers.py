from django.db import models


class TaskManager(models.Manager):
    def get_queryset(self):
        return super(TaskManager, self).get_queryset().prefetch_related('questions', 'questions__answers')

