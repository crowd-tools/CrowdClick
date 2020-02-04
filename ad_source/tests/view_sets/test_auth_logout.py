from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class TestAuthView(APITestCase):
    def setUp(self):
        self.url = reverse('logout_view')
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_user(username='admin', password='admin')

    def test_logout_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
