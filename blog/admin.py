from django.contrib import admin

from . import models


@admin.register(models.Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'image_url',
        'bio',
        'user',
    )


@admin.register(models.Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('title',),
    }
