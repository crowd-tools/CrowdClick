from ckeditor.fields import RichTextField
from django.contrib.auth import get_user_model
from django.db import models


class Author(models.Model):
    user = models.OneToOneField(get_user_model(), related_name='author_profile', on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    bio = RichTextField(blank=True, default='')
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    author = models.ForeignKey('Author', related_name='articles', on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=250)
    slug = models.SlugField()
    content = RichTextField()
    image_url = models.URLField()

    def __str__(self):
        return f'{self.title} ({self.author})'
