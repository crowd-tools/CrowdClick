from django.contrib import admin

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'website_link', 'og_image_link', 'time_duration', 'created', 'is_active', 'user')
    search_fields = ('title', 'user__username',)


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'get_question_type_display')
    search_fields = ('title', 'task__title', 'task__user__username')


@admin.register(models.Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')
    search_fields = ('title', 'question__title', 'question__task__user__username')


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'timestamp')
    readonly_fields = ('answered_questions', 'task')
    list_filter = ('user', 'task',)

    def answered_questions(self, obj: models.Answer):
        return ';'.join(obj.selected_options.values_list('question__title', flat=True))


@admin.register(models.Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'task', 'amount', 'timestamp')
    list_filter = ('sender', 'receiver', 'task',)
    search_fields = ('sender__username', 'receiver__username', 'task__title', 'task__user__username')


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')
    search_fields = ('email', )
