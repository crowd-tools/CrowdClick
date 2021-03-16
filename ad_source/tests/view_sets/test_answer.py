from django.urls import reverse
from rest_framework.test import APITestCase


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

    def test_create_answer_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 2)
        response = self.client.post(self.url, data=self.ANSWER_DATA)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'admin')
        response = self.client.get(self.list_url)
        data = response.json()
        self.assertEqual(data['count'], 1)

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
