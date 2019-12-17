from rest_framework import viewsets, mixins
from rest_framework.authentication import BasicAuthentication
from rest_framework import permissions

from . import serializers, models, authentication


class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = models.Option.objects.all()
    serializer_class = serializers.OptionSerializer


class SubscribeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Subscribe.objects.all()
    serializer_class = serializers.SubscribeSerializer
    permission_classes = permissions.AllowAny,
