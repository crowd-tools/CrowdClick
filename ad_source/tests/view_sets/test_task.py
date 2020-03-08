from django.urls import reverse
from rest_framework.test import APITestCase
import responses


class TestTaskView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']
    TASK_DATA = {
        "title": "Check our site",
        "description": "Awesome site. Go check it now and earn crypto",
        "website_link": "example.com",
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
    OG_DATA = """
<!DOCTYPE html>
<html>
  <head>
    <meta property="og:image" content="http://ogp.me/logo.png">
  </head>
  <body></body>
</html>
"""
    OG_DATA_2 = """
<!DOCTYPE html>
<html>
  <head></head>
  <body></body>
</html>
"""

    def setUp(self):
        self.url = reverse('task_view-list')

    def test_list_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_list_task_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_create_task_anon(self):
        response = self.client.post(self.url, data=self.TASK_DATA)
        self.assertEqual(response.status_code, 403)

    @responses.activate
    def test_create_task_admin(self):
        responses.add(responses.GET, 'http://example.com',
                      body=self.OG_DATA, status=200)
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.url, data=self.TASK_DATA)
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['website_link'], 'http://example.com')
        self.assertEqual(data['id'], 3)

    @responses.activate
    def test_create_task_admin_with_second_missing_og_data_is_none(self):
        responses.add(responses.GET, 'http://example.com',
                      body=self.OG_DATA, status=200)
        responses.add(responses.GET, 'http://example.com',
                      body=self.OG_DATA_2, status=200)
        self.client.login(username='admin', password='admin')
        self.client.post(self.url, data=self.TASK_DATA)
        response = self.client.post(self.url, data=self.TASK_DATA)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['website_link'], 'http://example.com')
        self.assertIsNone(data['og_image_link'])
