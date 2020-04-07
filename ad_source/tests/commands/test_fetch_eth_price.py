import datetime
from unittest import mock

import responses
from django.core.management import call_command
from django.test import TestCase

from ad_source.management.commands.fetch_eth_price import CACHE_KEY


class CommandsTestCase(TestCase):
    @mock.patch("ad_source.management.commands.fetch_eth_price.cache.get", lambda x:  {"eth_prices": {}})
    @mock.patch("ad_source.management.commands.fetch_eth_price.cache.delete")
    def test_drop(self, mock_delete):
        call_command('fetch_eth_price', '--drop')
        mock_delete.assert_called_once_with(CACHE_KEY)

    @responses.activate
    @mock.patch("ad_source.management.commands.fetch_eth_price.cache.get", lambda x, y: {})
    @mock.patch("ad_source.management.commands.fetch_eth_price.cache.set")
    def test_fetch(self, mock_set):
        responses.add(responses.GET, 'https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD',
                      body='{"USD": 150.00}', status=200)
        with mock.patch('ad_source.management.commands.fetch_eth_price.datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.date(2000, 12, 30)
            call_command('fetch_eth_price')
            mock_set.assert_called_once_with(CACHE_KEY, {'eth_prices': {'USD': 150.0}, 'last_updated': '2000-12-30'})
