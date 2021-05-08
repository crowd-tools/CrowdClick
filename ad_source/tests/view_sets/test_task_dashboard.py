from unittest.mock import patch

import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models
from ad_source.helpers import ETH2USD
from ad_source.tests.view_sets import ETH2USD_DATA

EXAMPLE_COM = '''
<!doctype html>
<html>
<head>
    <title>Example Domain</title>
</head>
<body>
<div>
    <h1>Example Domain</h1>
</div>
</body>
</html>
'''


class TestTaskDashboardView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']

    def setUp(self):
        self.list_url = reverse('task_dashboard-list')
        self.client.login(username='admin', password='admin')

    @responses.activate
    def test_get_dashboard_list(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['results'][0]['answers_result_count'], 0)

    @responses.activate
    def test_get_dashboard_detail(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        task = models.Task.objects.first()
        response = self.client.get(
            reverse('task_dashboard-detail', kwargs={'pk': task.id})
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['answers_result_count'], 0)

    @responses.activate
    def test_update_dashboard_detail(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)

        responses.add(responses.GET, 'https://example.com',
                      body=EXAMPLE_COM, status=200)
        data = {
            'website_link': 'https://example.com',
        }
        task = models.Task.objects.first()
        response = self.client.patch(
            reverse('task_dashboard-detail', kwargs={'pk': task.id}),
            data=data,
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['website_link'], 'https://example.com/')

    @responses.activate
    def test_withdraw_dashboard_detail(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_update_task:
            task = models.Task.objects.first()
            response = self.client.post(
                reverse('task_dashboard-withdraw', kwargs={'pk': task.id}),
            )
            data = response.json()
            self.assertEqual(response.status_code, status.HTTP_200_OK, data)
            self.assertEqual(data['website_link'], 'http://example.com')
            mock_update_task.assert_called_once_with(task_id=task.id, should_be_active=False, retry=5)
