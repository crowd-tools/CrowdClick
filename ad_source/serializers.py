from rest_framework import serializers

from .models import Advertisement, Question


class AdvertisementSerializer(serializers.HyperlinkedModelSerializer):

    questions = serializers.StringRelatedField(many=True)

    class Meta:
        model = Advertisement
        fields = [
            'website_link',
            'title',
            'description',
            'reward_per_click',
            'time_duration',

            'questions',
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.StringRelatedField(many=True)

    class Meta:
        model = Question
        fields = [
            'title',
            'question_type',

            'answers',
        ]
