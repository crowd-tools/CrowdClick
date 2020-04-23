import logging

import requests.exceptions
from rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from . import models
from .models import SelectedOption, AnsweredQuestion, Answer, Task, Option, Question
from .open_graph import OpenGraph
from .utils import convert_url

L = logging.getLogger(__name__)


class OptionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Option
        fields = [
            'id',
            'title',
            'url',
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
    warning_message = serializers.SerializerMethodField(read_only=True)

    def create(self, validated_data):
        questions = validated_data.pop('questions')
        task = Task.objects.create(**validated_data)
        for question in questions:
            q = Question.objects.create(title=question['title'], task=task)
            for option in question['options']:
                Option.objects.create(title=option['title'], question=q)
        return task

    def validate_website_link(self, website_link):
        return convert_url(website_link)

    def validate(self, attrs):
        website_link = attrs.get('website_link')
        if website_link:
            try:
                self._og = OpenGraph(url=website_link)
            except requests.exceptions.ConnectionError as e:
                L.warning(e)
                raise serializers.ValidationError({'website_link': f'Connection error for {website_link}'})
            attrs.update({
                'og_image_link': self._og.image,
                'website_link': self._og.RESOLVED_URL or website_link
            })
        return super().validate(attrs)

    def get_warning_message(self, obj):
        warning_msg = ''
        if hasattr(self, '_og'):  # from validate only
            og = self._og
            if og.X_FRAME_OPTIONS:
                # Website doesn't allow us to be viewed
                warning_msg = f'Website has strict X-Frame-Options: {og.X_FRAME_OPTIONS}'
        return warning_msg

    class Meta:
        model = models.Task
        fields = [
            'id',
            'title',
            'description',
            'user',
            'og_image_link',
            'website_link',
            'reward_per_click',
            'reward_usd_per_click',
            'spend_daily',
            'time_duration',
            'questions',
            'warning_message',
        ]


class TaskDashboardSerializer(TaskSerializer):
    answers_result_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Task
        fields = [
            'id',
            'title',
            'description',
            'user',
            'og_image_link',
            'website_link',
            'reward_per_click',
            'reward_usd_per_click',
            'spend_daily',
            'time_duration',
            'questions',
            'answers_result_count',
        ]


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Subscribe
        fields = [
            'email'
        ]


class SelectedOptionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = SelectedOption
        fields = [
            'id',
        ]


class AnsweredQuestionSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()
    options = SelectedOptionSerializer(many=True, source='selected_option')

    class Meta:
        model = AnsweredQuestion
        fields = [
            'id',
            'options',
        ]


class AnswerSerializer(serializers.HyperlinkedModelSerializer):
    task = TaskSerializer(read_only=True)
    questions = AnsweredQuestionSerializer(many=True, source='answered_questions')
    user = UserDetailsSerializer(read_only=True)
    timestamp = serializers.DateTimeField(read_only=True, allow_null=True)

    def create(self, validated_data):
        answered_questions = []
        for question in validated_data['answered_questions']:
            for option in question['selected_option']:
                selected_option = SelectedOption.objects.create(option_id=option['id'])
                answered_question = AnsweredQuestion.objects.create(
                    question_id=question['id'],
                    # selected_option=selected_option,
                )
                answered_question.selected_option.set([selected_option])
                answered_questions.append(answered_question)
        answer = Answer.objects.create(
            task=validated_data['task'],
            user=validated_data['user'],
        )
        answer.answered_questions.set(answered_questions)
        return answer

    class Meta:
        model = models.Answer
        fields = [
            'task',
            'user',
            'timestamp',
            'questions',
        ]
