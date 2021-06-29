from rest_framework import (
    viewsets,
    permissions,
)
from rest_framework.authentication import BasicAuthentication

from ad_source import authentication
from . import (
    models,
    serializers,
)


class AuthorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]

    def get_queryset(self):
        if self.request.user.is_superuser:
            qs = models.Author.objects.all()
        elif self.request.user.is_authenticated:
            qs = models.Author.objects.filter(user=self.request.user)
        else:
            qs = models.Author.objects.none()
        return qs


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ArticleSerializer
    queryset = models.Article.objects.all()
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
