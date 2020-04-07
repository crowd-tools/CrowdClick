from unittest import mock

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestSubscribeView(APITestCase):
    def setUp(self):
        self.url = reverse('eth_view-list')

    @mock.patch("ad_source.management.commands.fetch_eth_price.cache.get", lambda x, y: {"eth_prices": {}})
    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data, {'eth_prices': {}})
