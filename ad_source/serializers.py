import logging

import requests.exceptions
from django.conf import settings
from djmoney.contrib.django_rest_framework import MoneyField
from djmoney.contrib.exchange.models import Rate
from rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers, status

from . import models, tasks
from .open_graph import OpenGraph
from .utils import convert_url

L = logging.getLogger(__name__)


class OptionSerializer(serializers.HyperlinkedModelSerializer):
    answer_count = serializers.IntegerField(read_only=True)
    is_correct = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = models.Option
        fields = [
            'id',
            'title',
            'url',
            'answer_count',
            'is_correct',
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
    tx_hash = serializers.CharField(source='initial_tx_hash', required=False)
    type = serializers.CharField(read_only=True)
    reward_per_click = MoneyField(max_digits=11, decimal_places=5)
    reward_usd_per_click = MoneyField(max_digits=11, decimal_places=5, read_only=True)
    remaining_balance = MoneyField(max_digits=9, decimal_places=3, read_only=True)
    initial_budget = MoneyField(max_digits=9, decimal_places=3, required=False)

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
            'website_image',
            'contract_address',
            'reward_per_click',
            'reward_usd_per_click',
            'time_duration',
            'questions',
            'warning_message',
            'is_active',
            'remaining_balance',
            'initial_budget',
            'tx_hash',
            'type',
        ]
        read_only_fields = [
            'user',
            'og_image_link',
            'remaining_balance',
            'website_image',
            'warning_message',
            'is_active',
        ]

    def create(self, validated_data):
        validated_data['is_active_web3'] = False
        questions = validated_data.pop('questions')
        task = super(TaskSerializer, self).create(validated_data)
        for question in questions:
            q = models.Question.objects.create(title=question['title'], task=task)
            for option in question['options']:
                models.Option.objects.create(
                    title=option['title'],
                    question=q,
                    is_correct=option.get('is_correct', False)
                )
        if task.initial_tx_hash:
            tasks.update_task_is_active_balance.delay(task_id=task.id, wait_for_tx=str(task.initial_tx_hash))
        else:
            tasks.update_task_is_active_balance.delay(
                task_id=task.id, should_be_active=True, retry=settings.WEB3_RETRY
            )
        tasks.create_task_screenshot.delay(task.id)
        return task

    def validate_website_link(self, website_link):
        return convert_url(website_link)

    def validate_questions(self, questions):
        for question in questions:
            # Validate number of correct options is max one
            correct_question_sum = sum([option.get('is_correct', False) for option in question.get('options', [])])
            if not correct_question_sum <= 1:
                raise serializers.ValidationError({
                    'question': f"Question {question.get('title', '')} has {correct_question_sum} correct questions."})
        return questions

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
    tx_hash = serializers.CharField(source='initial_tx_hash', required=False)
    type = serializers.CharField(read_only=True)
    reward_per_click = MoneyField(max_digits=11, decimal_places=5)
    remaining_balance = MoneyField(max_digits=9, decimal_places=3, required=False)
    initial_budget = MoneyField(max_digits=9, decimal_places=3, required=False)

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
            'reward_per_click',
            'reward_usd_per_click',
            'time_duration',
            'questions',
            'answers_result_count',
            'answers',
            'remaining_balance',
            'initial_budget',
            'tx_hash',
            'type',
        ]


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Subscribe
        fields = [
            'email'
        ]


class RateSerializer(serializers.ModelSerializer):
    last_update = serializers.SerializerMethodField()

    class Meta:
        model = Rate
        fields = [
            'currency',
            'value',
            'last_update',
        ]

    def get_last_update(self, instance: Rate):
        return instance.backend.last_update
