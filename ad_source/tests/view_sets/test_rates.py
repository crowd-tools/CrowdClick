import unittest.mock

import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source.tests import mixins


class TestSubscribeView(mixins.RateMixin, APITestCase):
    def setUp(self):
        self.url = reverse('rates-list')

    @responses.activate
    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(len(data), 3)
        self.assertEqual(list(data[0].keys()), ['currency', 'value', 'value_to_usd', 'last_update'])
        self.assertEqual(list(data[0].values()), ['BNB', '0.003600', 277.77777777777777, unittest.mock.ANY])
