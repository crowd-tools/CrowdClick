from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models
from ad_source.tests import mixins


class TestQuestionView(mixins.DataTestMixin, APITestCase):

    def setUp(self):
        self.url = reverse('question-list')
        self.question = models.Question.objects.first()
        self.detail_url = reverse('question-detail', kwargs={'pk': self.question.id})

    def test_delete_question_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_question_user(self):
        self.client.login(username='0xa1f765189805e0e51ac9753a9bc7d99e2b90c705', password='user')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_question_anon(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
