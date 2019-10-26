from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication

from . import serializers, models, authentication


class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer

