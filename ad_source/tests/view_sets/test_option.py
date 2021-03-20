from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models


class TestOptionView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']

    def setUp(self):
        self.url = reverse('option-list')
        self.option = models.Option.objects.first()
        self.detail_url = reverse('option-detail', kwargs={'pk': self.option.id})

    def test_delete_option_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_option_user(self):
        self.client.login(username='0xa1f765189805e0e51ac9753a9bc7d99e2b90c705', password='admin')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_option_anon(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
