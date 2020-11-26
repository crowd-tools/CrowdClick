from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models


class TestTaskDashboardView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']

    def setUp(self):
        self.list_url = reverse('task_dashboard-list')
        self.client.login(username='admin', password='admin')

    def test_get_dashboard_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['results'][0]['answers_result_count'], 0)

    def test_get_dashboard_detail(self):
        task = models.Task.objects.first()
        response = self.client.get(
            reverse('task_dashboard-detail', kwargs={'pk': task.id})
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['answers_result_count'], 0)

    def test_update_dashboard_detail(self):
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
