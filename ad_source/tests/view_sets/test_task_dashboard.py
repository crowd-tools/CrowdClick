from django.urls import reverse
from rest_framework.test import APITestCase


class TestTaskDashboardView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']

    def setUp(self):
        self.url = reverse('task_view-task_dashboard')

    def test_get_dashboard_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.data[0]['answers_result_count'], 0)
