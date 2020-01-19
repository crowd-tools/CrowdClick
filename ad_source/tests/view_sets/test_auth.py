from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


class TestAuthView(APITestCase):
    def setUp(self):
        self.url = reverse('auth_view')
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_user(username='admin', password='admin')

    def test_get_auth_anon(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_authenticated'], False)
        self.assertIsNotNone(response.data['nonce'])
        self.assertRaises(KeyError, lambda: response.data['username'])

    def test_get_auth_admin(self):
        self.client.login(username='admin', password='admin')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_authenticated'], True)
        self.assertEqual(response.data['username'], 'admin')
        self.assertRaises(KeyError, lambda: response.data['nonce'])

    @patch('sha3.keccak_256')
    def test_post_auth_token(self, mock_sha3_class):
        session = self.client.session
        session['login_nonce'] = "deadbeef"
        session.save()

        recovered_addr = 'deadc0dedeadc0dedeadc0dedeadc0dedeadc0de'
        mock_sha3 = MagicMock()
        mock_sha3_class.return_value = mock_sha3
        mock_sha3.hexdigest.return_value = recovered_addr

        data = {
            "user_address": "0xdeadc0dedeadc0de",
            "user_signature": "0x" + "0" * 130
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_authenticated'], True)
        self.assertEqual(response.data['username'], '0xdeadc0dedeadc0de')
        self.assertEqual(response.data['created'], True)

    def test_post_auth_token_without_session(self):
        data = {
            "user_address": "0xdeadc0dedeadc0de",
            "user_signature": "0x" + "0" * 130
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['login_nonce'], "Session id doesn't have a `login_nonce`")

    def test_post_auth_token_without_user_address(self):
        session = self.client.session
        session['login_nonce'] = "deadbeef"
        session.save()

        data = {
            "user_signature": "0x" + "0" * 130
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['user_address'], "Request doesn't have a `user_address`")

    def test_post_auth_token_without_user_signature(self):
        session = self.client.session
        session['login_nonce'] = "deadbeef"
        session.save()

        data = {
            "user_address": "0xdeadc0dedeadc0de",
        }

        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['user_signature'], "Request doesn't have a `user_signature`")

    def test_post_auth_token_token_doesnt_match(self):
        session = self.client.session
        session['login_nonce'] = "deadbeef"
        session.save()

        data = {
            "user_address": "0xdeadc0dedeadc0de",
            "user_signature": "0x" + "0" * 130
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['user_signature'], "User signature doesn't match `user_address`")
