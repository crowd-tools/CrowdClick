import abc

from rest_framework import serializers

from . import models

# TODO delete


class QuestionAnswerRelatedField(serializers.RelatedField, abc.ABC):
    def get_queryset(self):
        return models.Option.objects.all()

    def to_representation(self, value):
        return {
            "id": value.id,
            "title": value.title,
        }


class TaskQuestionRelatedField(serializers.RelatedField, abc.ABC):
    answers = QuestionAnswerRelatedField(many=True)

    def get_queryset(self):
        return models.Question.objects.all()

    def to_representation(self, value):
        result = {
            "id": value.id,
            "title": value.title,
            "type": value.question_type,
            "result_count": value.result_count,
            "answers": []
        }
        for answer in value.answers.all():
            result["answers"].append({
                "id": answer.id,
                "title": answer.title,
            })
        return result

    def to_internal_value(self, data):
        ad = models.Task.objects.all().order_by('-id')[0]
        question = models.Question.objects.create(title=data.get("title"), question_type=data.get("type"), ad=ad)
        for answer in data.get("answer", []):
            models.Option.objects.create(title=answer.get("title"), question=question)
        return question
