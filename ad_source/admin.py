from django.contrib import admin

from . import models


@admin.register(models.Subscribe)
class AtrAdmin(admin.ModelAdmin):
    list_display = ('email', 'timestamp')
