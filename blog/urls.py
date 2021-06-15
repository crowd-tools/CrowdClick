from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from . import view_sets

if settings.DEBUG:
    router_class = routers.DefaultRouter
else:
    router_class = routers.SimpleRouter

router = router_class()

router.register('author', view_sets.AuthorViewSet, basename='author_view')
router.register('article', view_sets.ArticleViewSet, basename='article_view')

urlpatterns = [
    path('', include(router.urls)),
]
