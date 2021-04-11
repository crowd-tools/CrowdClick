from unittest.mock import patch

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ad_source import models


class RewardViewSetTestCase(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']

    def setUp(self) -> None:
        self.task = models.Task.objects.get(id=1)
        self.url = reverse('reward_view-list', kwargs={'task_id': self.task.id})
        self.admin = models.User.objects.get(username='admin')

    @patch('web3.eth.Eth.sendRawTransaction')
    @patch('ad_source.web3_providers.Web3.toChecksumAddress')
    def test_create_reward(self, w3_checksum_mock, w3_send_transaction_mock):
        answer = models.Answer.objects.create(
            user=self.admin,
            task=self.task,
        )
        self.task.answers.add(answer)
        web3_checksum_side_effects = {
            'admin': '0xDd2179e8D8755f810CdAe4a474F7c53F371FbB6A',
        }

        def web3_checksum_side_effect(val):
            return web3_checksum_side_effects[val]

        w3_checksum_mock.side_effect = web3_checksum_side_effect
        w3_send_transaction_mock.return_value = b'a' * 5
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_task:
            self.client.login(username='admin', password='admin')
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {'tx_hash': '6161616161'})

            self.assertEqual(w3_checksum_mock.call_count, 2)
            self.assertEqual(w3_send_transaction_mock.call_count, 1)

            # test reward again
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(response.json(), {"error": "Reward already created"})
            self.assertEqual(w3_checksum_mock.call_count, 2)
            self.assertEqual(w3_send_transaction_mock.call_count, 1)

            mock_task.assert_called_once_with(self.task.id)

    def test_create_reward_without_answers(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reward_unauthenticated(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_reward_bad_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RewardQuizViewSetTestCase(APITestCase):
    fixtures = ['0000_users', '0001_task', '0002_question', '0003_options']

    def setUp(self) -> None:
        self.task = models.Task.objects.get(id=3)
        self.url = reverse('reward_view-list', kwargs={'task_id': self.task.id})
        self.admin = models.User.objects.get(username='admin')
        self.option = models.Option.objects.get(id=5)
        self.wrong_option = models.Option.objects.get(id=6)

    @patch('web3.eth.Eth.sendRawTransaction')
    @patch('ad_source.web3_providers.Web3.toChecksumAddress')
    def test_create_reward(self, w3_checksum_mock, w3_send_transaction_mock):
        answer = models.Answer.objects.create(
            user=self.admin,
            task=self.task,
        )
        answer.selected_options.set([self.option])
        self.task.answers.add(answer)
        web3_checksum_side_effects = {
            'admin': '0xDd2179e8D8755f810CdAe4a474F7c53F371FbB6A',
        }

        def web3_checksum_side_effect(val):
            return web3_checksum_side_effects[val]

        w3_checksum_mock.side_effect = web3_checksum_side_effect
        w3_send_transaction_mock.return_value = b'a' * 5
        with patch('ad_source.tasks.update_task_is_active_balance.delay') as mock_task:
            self.client.login(username='admin', password='admin')
            response = self.client.post(self.url)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {'tx_hash': '6161616161'})

            self.assertEqual(w3_checksum_mock.call_count, 2)
            self.assertEqual(w3_send_transaction_mock.call_count, 1)

            mock_task.assert_called_once_with(self.task.id)

    def test_create_reward_wrong_answer(self):
        answer = models.Answer.objects.create(
            user=self.admin,
            task=self.task,
        )
        answer.selected_options.set([self.wrong_option])
        self.task.answers.add(answer)

        self.client.login(username='admin', password='admin')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())
