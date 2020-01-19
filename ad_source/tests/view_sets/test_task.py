from django.urls import reverse
from rest_framework.test import APITestCase


class TestTaskView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']
    TASK_DATA = {
        "title": "Check our site",
        "description": "Awesome site. Go check it now and earn crypto",
        "website_link": "http://example.com",
        "reward_per_click": 0.001,
        "time_duration": "00:00:30",
        "spend_daily": 1,
        "questions": [
            {
                "title": "Was it good?",
                "options": [
                    {"title": "Good"},
                    {"title": "Bad"}
                ]
            }
        ]
    }

    def setUp(self):
        self.url = reverse('task_view-list')

    def test_list_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_list_task_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_create_task_anon(self):
        response = self.client.post(self.url, data=self.TASK_DATA)
        self.assertEqual(response.status_code, 403)

    def test_create_task_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.url, data=self.TASK_DATA)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'], 3)
