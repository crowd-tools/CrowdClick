from django.contrib import admin

from . import models


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'description')


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'timestamp')
    readonly_fields = ('answered_questions', 'task')

    def answered_questions(self, obj: models.Answer):
        return ';'.join(obj.selected_options.values_list('question__title', flat=True))
