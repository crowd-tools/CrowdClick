import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source.helpers import ETH2USD
from ad_source.tests.view_sets import ETH2USD_DATA


class TestSubscribeView(APITestCase):
    def setUp(self):
        self.url = reverse('eth_view-list')

    @responses.activate
    def test_get(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data, {})
