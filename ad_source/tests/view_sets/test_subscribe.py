from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ...models import Subscribe


class TestSubscribeView(APITestCase):
    def setUp(self):
        self.url = reverse('subscribe-list')

    def test_create_subscribe(self):
        data = {'email': 'foo@bar.com'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Subscribe.objects.count(), 1)
        self.assertEqual(Subscribe.objects.get().email, 'foo@bar.com')

    def test_get_subscribe(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
