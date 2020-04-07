import datetime
import logging

import requests
from django.core.cache import cache
from django.core.management.base import BaseCommand

URL = 'https://min-api.cryptocompare.com/data/price?fsym={from_symbol}&tsyms={to_symbol}'
CACHE_KEY = 'ETH-PRICES'

Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch price of ETH and stores to memcache'

    def add_arguments(self, parser):
        parser.add_argument('--from', type=str, default='ETH')
        parser.add_argument('--to', type=str, default='USD')
        parser.add_argument('--print', action='store_true', default=False,
                            help=f'If specified, prints `{CACHE_KEY}` only')
        parser.add_argument('--drop', action='store_true', default=False,
                            help=f'If specified, drops `{CACHE_KEY}` only')

    def handle(self, *args, **options):
        # Print
        if options.get('print'):
            Logger.warning(cache.get(CACHE_KEY))
            return
        # Drop
        if options.get('drop'):
            value = cache.get(CACHE_KEY)
            if value:
                cache.delete(CACHE_KEY)
                Logger.warning(f"Dropped: {value}")
            return
        # Fetch
        # https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD
        url = URL.format(from_symbol=options['from'], to_symbol=options['to'])
        response = requests.get(url)
        data = response.json()

        cache_dict = cache.get(CACHE_KEY, {})
        if 'eth_prices' not in cache_dict:
            cache_dict['eth_prices'] = {}
        cache_dict.update({"last_updated": datetime.datetime.now().isoformat()})
        for key, value in data.items():
            cache_dict['eth_prices'].update({key: value})

        cache.set(CACHE_KEY, cache_dict)
