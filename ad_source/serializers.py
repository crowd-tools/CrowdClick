from rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

from . import models
from .models import SelectedOption, AnsweredQuestion, Answer


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
    image_thumbnail = serializers.ImageField(read_only=True)
    image = serializers.ImageField(read_only=True)
    user = UserDetailsSerializer(read_only=True)

    class Meta:
        model = models.Task
        fields = [
            'id',
            'title',
            'description',
            'user',
            'image',
            'image_thumbnail',
            'website_link',
            'reward_per_click',
            'reward_usd_per_click',
            'spend_daily',
            'time_duration',
            'questions',
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
            'image',
            'image_thumbnail',
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
