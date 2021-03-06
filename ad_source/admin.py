from django.contrib import admin

from . import models


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'website_link', 'og_image_link', 'time_duration', 'created', 'is_active', 'user')


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'get_question_type_display')


@admin.register(models.Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'timestamp')
    readonly_fields = ('answered_questions', 'task')

    def answered_questions(self, obj: models.Answer):
        return ';'.join(obj.selected_options.values_list('question__title', flat=True))


@admin.register(models.Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'task', 'amount', 'timestamp')


@admin.register(models.Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')
