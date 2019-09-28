from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication

from . import serializers, models, authentication


class AdvertisementViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Advertisement.objects.all()
    serializer_class = serializers.AdvertisementSerializer


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer

