import responses
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models

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
        responses.add(responses.GET, settings.ETH2USD_URL.format(from_symbol='ETH', to_symbol='USD'),
                      body='{"USD": 2099.65}', status=200)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['results'][0]['answers_result_count'], 0)

    @responses.activate
    def test_get_dashboard_detail(self):
        responses.add(responses.GET, settings.ETH2USD_URL.format(from_symbol='ETH', to_symbol='USD'),
                      body='{"USD": 2099.65}', status=200)
        task = models.Task.objects.first()
        response = self.client.get(
            reverse('task_dashboard-detail', kwargs={'pk': task.id})
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['answers_result_count'], 0)

    @responses.activate
    def test_update_dashboard_detail(self):
        responses.add(responses.GET, settings.ETH2USD_URL.format(from_symbol='ETH', to_symbol='USD'),
                      body='{"USD": 2099.65}', status=200)

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
