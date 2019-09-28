import abc

from rest_framework import serializers

from . import models


class QuestionAnswerRelatedField(serializers.RelatedField, abc.ABC):
    def get_queryset(self):
        return models.Answer.objects.all()

    def to_representation(self, value):
        return {
            "id": value.id,
            "title": value.title,
        }


class AdvertisementQuestionRelatedField(serializers.RelatedField, abc.ABC):
    answers = QuestionAnswerRelatedField(many=True)

    def get_queryset(self):
        return models.Question.objects.all()

    def to_representation(self, value):
        result = {
            "id": value.id,
            "title": value.title,
            "type": value.question_type,
            "answers": []
        }
        for answer in value.answers.all():
            result["answers"].append({
                "id": answer.id,
                "title": answer.title,
            })
        return result
