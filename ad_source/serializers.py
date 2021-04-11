import logging

import requests.exceptions
from rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers, status

from . import models, tasks
from .open_graph import OpenGraph
from .utils import convert_url

L = logging.getLogger(__name__)


class OptionSerializer(serializers.HyperlinkedModelSerializer):
    answer_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Option
        fields = [
            'id',
            'title',
            'url',
            'answer_count',
        ]


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = models.Question
        fields = [
            'id',
            'title',
            'url',
            'options',
        ]


class TaskSerializer(serializers.HyperlinkedModelSerializer):
    questions = QuestionSerializer(many=True)
    og_image_link = serializers.URLField(read_only=True)
    user = UserDetailsSerializer(read_only=True)

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        task = super(TaskSerializer, self).create(validated_data)
        for question in questions:
            q = models.Question.objects.create(title=question['title'], task=task)
            for option in question['options']:
                models.Option.objects.create(title=option['title'], question=q)
        tasks.update_task_is_active_balance.delay(task.id)
        return task

    def validate_website_link(self, website_link):
        return convert_url(website_link)

    def validate(self, attrs):
        website_link = attrs.get('website_link')
        if website_link:
            try:
                og = OpenGraph(url=website_link)
            except requests.exceptions.ConnectionError as e:
                L.warning(e)
                raise serializers.ValidationError({'website_link': f'Connection error for {website_link}'})
            if og.response.status_code != status.HTTP_200_OK:
                message = f'Website {website_link} responded with status code: {og.response.status_code}'
                L.warning(message)
                # raise serializers.ValidationError({'website_link': f'{message}. Has to be 200'})
            attrs.update({
                'og_image_link': og.image,
                'website_link': og.RESOLVED_URL or website_link,
            })
            if og.X_FRAME_OPTIONS:
                attrs.update({
                    'warning_message': f'Website has strict X-Frame-Options: {og.X_FRAME_OPTIONS}',
                })
        return super().validate(attrs)

    class Meta:
        model = models.Task
        fields = [
            'id',
            'title',
            'description',
            'chain',
            'user',
            'og_image_link',
            'uuid',
            'website_link',
            'contract_address',
            'reward_per_click',
            'reward_usd_per_click',
            'time_duration',
            'questions',
            'warning_message',
            'is_active'
        ]
        read_only_fields = [
            'remaining_balance',
        ]


class SelectedOptionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField(read_only=True)

    class Meta:
        model = models.Option
        fields = [
            'id',
            'title',
        ]


class AnsweredQuestionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    options = SelectedOptionSerializer(many=True)

    class Meta:
        model = models.Answer
        fields = [
            'id',
            'options',
        ]


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    user = UserDetailsSerializer(read_only=True)
    questions = AnsweredQuestionSerializer(many=True, source='answered_questions')
    selected_options = OptionSerializer(many=True, read_only=True)
    timestamp = serializers.DateTimeField(read_only=True, allow_null=True)

    class Meta:
        model = models.Answer
        fields = [
            'user',
            'selected_options',
            'questions',
            'timestamp',
        ]

    def create(self, validated_data):
        selected_options = []
        for question in validated_data['answered_questions']:
            for option in question['options']:
                selected_options.append(option['id'])
        answer = models.Answer.objects.create(
            task=validated_data['task'],
            user=validated_data['user'],
        )
        answer.selected_options.set(selected_options)
        return answer


class TaskDashboardSerializer(TaskSerializer):
    answers_result_count = serializers.IntegerField(read_only=True)
    answers = AnswerSerializer(many=True)

    class Meta:
        model = models.Task
        fields = [
            'id',
            'title',
            'description',
            'chain',
            'user',
            'og_image_link',
            'website_link',
            'reward_per_click',
            'reward_usd_per_click',
            'time_duration',
            'questions',
            'answers_result_count',
            'answers',
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscribe
        fields = [
            'email'
        ]
