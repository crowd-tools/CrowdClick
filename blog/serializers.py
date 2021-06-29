from django.utils.text import slugify
from rest_framework import serializers

from . import models


class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Author
        fields = (
            'user',
            'name',
            'bio',
            'image_url',
        )
        read_only_fields = (
            'user',
        )

    def validate(self, attrs):
        if not attrs['name']:
            raise serializers.ValidationError(detail={'name': 'Name is required'})
        request = self.context['request']
        if request.user.is_authenticated:
            attrs['user'] = request.user
        return attrs


class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = models.Article
        fields = (
            'slug',
            'author',
            'created',
            'modified',
            'title',
            'content',
            'image_url',
        )
        read_only_fields = (
            'slug',
        )

    def validate(self, attrs):
        request = self.context['request']
        try:
            author = models.Author.objects.get(user=request.user)
        except models.Author.DoesNotExist:
            raise serializers.ValidationError(detail={'author': 'Author Profile does not exist.'})
        attrs['author'] = author
        attrs['slug'] = slugify(attrs['title'])
        return attrs
