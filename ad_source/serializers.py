from rest_framework import serializers

from . import models


class AnswerSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Option
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
    image_thumbnail = serializers.ImageField(read_only=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = models.Task
        fields = [
            'id',
            'title',
            'description',
            'image',
            'image_thumbnail',
            'website_link',
            'reward_per_click',
            'reward_usd_per_click',
            'spend_daily',
            'time_duration',
            'questions',
        ]


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Subscribe
        fields = [
            'email'
        ]
