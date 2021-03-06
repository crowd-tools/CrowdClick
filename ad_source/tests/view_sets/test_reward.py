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

    @patch('web3.eth.Eth.sendRawTransaction')
    @patch('ad_source.view_sets.Web3.toChecksumAddress')
    def test_create_reward(self, w3_checksum_mock, w3_send_transaction_mock):
        web3_checksum_side_effects = {
            'admin': '0xDd2179e8D8755f810CdAe4a474F7c53F371FbB6A',
        }

        def web3_checksum_side_effect(val):
            return web3_checksum_side_effects[val]

        w3_checksum_mock.side_effect = web3_checksum_side_effect
        w3_send_transaction_mock.return_value = b'a' * 5

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
