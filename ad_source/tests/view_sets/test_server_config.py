from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestSubscribeView(APITestCase):
    def setUp(self):
        self.url = reverse('server_config-list')

    def test_get_server_config(self):
        expected = {'public_key': settings.ACCOUNT_OWNER_PUBLIC_KEY}
        response = self.client.get(self.url)
        data = response.json()
        self.assertEqual(data, expected)

    def test_create_server_config(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_server_config(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
