import responses
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source.helpers import ETH2USD
from ad_source.tests.view_sets import ETH2USD_DATA


class TestAnswerView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']
    ANSWER_DATA = {
        "questions": [
            {
                "id": 1,
                "options": [{"id": 1}]
            },
            {
                "id": 2,
                "options": [{"id": 3}]
            }
        ]
    }

    def setUp(self):
        self.url = reverse('task_view-task_answer', kwargs={'pk': 1})
        self.list_url = reverse('task_view-list')

    def test_create_answer_anon(self):
        response = self.client.post(self.url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 403)

    @responses.activate
    def test_create_answer_admin(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 3)
        response = self.client.post(self.url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 2)

    def test_create_answer_task_id_not_int(self):
        self.client.login(username='admin', password='admin')
        url = reverse('task_view-task_answer', kwargs={'pk': "foo"})
        response = self.client.post(url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 400)

    def test_create_answer_task_doesnt_exist(self):
        self.client.login(username='admin', password='admin')
        url = reverse('task_view-task_answer', kwargs={'pk': 666})
        response = self.client.post(url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 404)

    def test_create_answer_for_different_task(self):
        self.client.login(username='admin', password='admin')
        url = reverse('task_view-task_answer', kwargs={'pk': 2})
        response = self.client.post(url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 404)

    def test_create_answer_wrong_options(self):
        self.client.login(username='admin', password='admin')
        data = self.ANSWER_DATA.copy()
        data['questions'][0]['options'][0]['id'] = 5
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 404)

    def test_delete_answer_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_answer_user(self):
        self.client.login(username='0xa1f765189805e0e51ac9753a9bc7d99e2b90c705', password='admin')
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_answer_anon(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestQuizAnswerView(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']
    WRONG_ANSWER_DATA = {
        "questions": [
            {
                "id": 3,
                "options": [{"id": 6}]
            }
        ]
    }
    ANSWER_DATA = {
        "questions": [
            {
                "id": 3,
                "options": [{"id": 5}]
            }
        ]
    }

    def setUp(self):
        self.url = reverse('task_view-task_answer', kwargs={'pk': 3})
        self.list_url = reverse('task_view-list')

    @responses.activate
    def test_create_correct_admin(self):
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 3)
        response = self.client.post(self.url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 2)

    @responses.activate
    def test_create_wrong_admin(self):
        # Creating wrong answer is allowed. Task will get hidden
        responses.add(responses.GET, ETH2USD.BASE_URL, body=ETH2USD_DATA, status=200)
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 3)
        response = self.client.post(self.url, data=self.WRONG_ANSWER_DATA)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 2)
