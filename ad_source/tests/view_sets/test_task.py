from unittest.mock import patch

import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models
from ad_source.tests import mixins


class TestTaskView(mixins.DataTestMixin, APITestCase):
    TASK_DATA = {
        "title": "Check our site",
        "description": "Awesome site. Go check it now and earn crypto",
        "uuid": "d8f01220-4c85-4b35-a3e2-9ff33858a6e7",
        "website_link": "does_not_exist.com",
        "contract_address": "0xdeadc0dedeadc0de",
        "reward_per_click": 0.001,
        "time_duration": "00:00:30",
        "tx_hash": "0xdeadc0dedeadc0de",
        "chain": "goerli",
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

    def setUp(self):
        self.url = reverse('task_view-list')
        self.published_task = models.Task.objects.get(pk=1)
        self.detail_url = reverse('task_view-detail', kwargs={'pk': self.published_task.id})

    @responses.activate
    def test_list_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        for result in response.data['results']:
            if result['id'] == 3:
                self.assertEqual(result['type'], 'quiz')
            else:
                self.assertEqual(result['type'], 'campaign')

    @responses.activate
    def test_filter_tasks_by_chain(self):
        response = self.client.get(self.url, data={"chain": "mumbai"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    @responses.activate
    def test_list_task_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)

    @responses.activate
    def test_list_campaign_admin(self):
        # List tasks that are not quiz
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url, data={'type': 'campaign'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    @responses.activate
    def test_list_quiz_admin(self):
        # List tasks that are quiz
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url, data={'type': 'quiz'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

    def test_create_task_anon(self):
        response = self.client.post(self.url, data=self.TASK_DATA)
        self.assertEqual(response.status_code, 403)

    @responses.activate
    def test_create_task_admin(self):
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_update_task:
            with patch('ad_source.tasks.create_task_screenshot.delay') as mock_screenshot_task:
                responses.add(responses.GET, 'http://does_not_exist.com',
                              body=self.OG_DATA, status=200)
                self.client.login(username='admin', password='admin')
                response = self.client.post(self.url, data=self.TASK_DATA)
                data = response.json()
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['website_link'], 'http://does_not_exist.com/')
                self.assertEqual(data['id'], 4)
                self.assertEqual(data['uuid'], 'd8f01220-4c85-4b35-a3e2-9ff33858a6e7')
                mock_update_task.assert_called_once_with(task_id=4, wait_for_tx='0xdeadc0dedeadc0de')
                mock_screenshot_task.assert_called_once_with(4)

    @responses.activate
    def test_create_task_admin_without_tx_hash(self):
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_update_task:
            with patch('ad_source.tasks.create_task_screenshot.delay') as mock_screenshot_task:
                responses.add(responses.GET, 'http://does_not_exist.com',
                              body=self.OG_DATA, status=200)
                data = self.TASK_DATA
                del data['tx_hash']
                self.client.login(username='admin', password='admin')
                response = self.client.post(self.url, data=data)
                data = response.json()
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['website_link'], 'http://does_not_exist.com/')
                self.assertEqual(data['id'], 4)
                self.assertEqual(data['uuid'], 'd8f01220-4c85-4b35-a3e2-9ff33858a6e7')
                mock_update_task.assert_called_once_with(task_id=4, should_be_active=True, retry=10)
                mock_screenshot_task.assert_called_once_with(4)

    @responses.activate
    def test_create_quiz_task_admin(self):
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_update_task:
            with patch('ad_source.tasks.create_task_screenshot.delay') as mock_screenshot_task:
                data = self.TASK_DATA
                data['questions'][0]['options'][0]['is_correct'] = True
                responses.add(responses.GET, 'http://does_not_exist.com',
                              body=self.OG_DATA, status=200)
                self.client.login(username='admin', password='admin')
                response = self.client.post(self.url, data=data)
                data = response.json()
                self.assertEqual(response.status_code, 201)
                self.assertEqual(data['website_link'], 'http://does_not_exist.com/')
                self.assertEqual(data['id'], 4)
                self.assertEqual(data['uuid'], 'd8f01220-4c85-4b35-a3e2-9ff33858a6e7')
                mock_update_task.assert_called_once_with(task_id=4, wait_for_tx='0xdeadc0dedeadc0de')
                mock_screenshot_task.assert_called_once_with(4)

    @responses.activate
    def test_create_task_admin_with_duplicates(self):
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_task:
            with patch('ad_source.tasks.create_task_screenshot.delay') as mock_screenshot_task:
                responses.add(responses.GET, 'http://does_not_exist.com',
                              body=self.OG_DATA, status=200)
                self.client.login(username='admin', password='admin')
                response = self.client.post(self.url, data=self.TASK_DATA)
                self.assertEqual(response.status_code, status.HTTP_201_CREATED)
                response = self.client.post(self.url, data=self.TASK_DATA)
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn('uuid', response.json())

                mock_task.assert_called_once_with(task_id=4, wait_for_tx='0xdeadc0dedeadc0de')
                mock_screenshot_task.assert_called_once_with(4)

    def test_create_task_admin_with_connection_error(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.url, data=self.TASK_DATA)
        data = response.json()
        self.assertEqual(['Connection error for http://does_not_exist.com'], data['website_link'])

    @responses.activate
    def test_create_task_admin_with_iframe_forbidden(self):
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_task:
            with patch('ad_source.tasks.create_task_screenshot.delay') as mock_screenshot_task:
                responses.add(responses.GET, 'http://does_not_exist.com',
                              body=self.OG_DATA, status=200,
                              headers={'X-Frame-Options': 'DENY'},)
                self.client.login(username='admin', password='admin')
                response = self.client.post(self.url, data=self.TASK_DATA)
                data = response.json()
                self.assertEqual(response.status_code, 201)
                self.assertEqual('Website has strict X-Frame-Options: deny', data['warning_message'])
                mock_task.assert_called_once_with(task_id=4, wait_for_tx='0xdeadc0dedeadc0de')
                mock_screenshot_task.assert_called_once_with(4)

    def test_delete_task_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @responses.activate
    def test_delete_task_user(self):
        self.client.login(username='0xa1f765189805e0e51ac9753a9bc7d99e2b90c705', password='admin')
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_task_anon(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestUserTaskView(mixins.DataTestMixin, APITestCase):

    @responses.activate
    def test_list_user_tasks(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(
            reverse('user_tasks_view', kwargs={'contract_address': '0xdeadc0dedeadc0de'})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        for task in data:
            self.assertEqual(task['contract_address'], '0xdeadc0dedeadc0de')
            self.assertEqual(task['user']['username'], 'admin')

    def test_list_user_tasks_forbidden(self):
        response = self.client.get(
            reverse('user_tasks_view', kwargs={'contract_address': '0xdeadc0dedeadc0de'})
        )
        self.assertEqual(response.status_code, 403)
