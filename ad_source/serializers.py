from rest_framework import serializers

from . import models


class AnswerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Answer
        fields = [
            'id',
            'title',
            'result_count',
            'url',
        ]


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = models.Question
        fields = [
            'id',
            'title',
            'url',
            'result_count',
            'answers',
        ]


class TaskSerializer(serializers.HyperlinkedModelSerializer):

    # questions = fields.TaskQuestionRelatedField(many=True)
    questions = QuestionSerializer(many=True)

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


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Subscribe
        fields = [
            'email'
        ]
