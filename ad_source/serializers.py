from rest_framework import serializers

from . import fields, models


class AdvertisementSerializer(serializers.HyperlinkedModelSerializer):

    questions = fields.AdvertisementQuestionRelatedField(many=True)

    class Meta:
        model = models.Task
        fields = [
            'id',
            'website_link',
            'title',
            'description',
            'reward_per_click',
            'time_duration',

            'questions',
        ]


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    answers = fields.QuestionAnswerRelatedField(many=True)

    class Meta:
        model = models.Question
        fields = [
            'id',
            'title',
            'question_type',

            'answers',
        ]
