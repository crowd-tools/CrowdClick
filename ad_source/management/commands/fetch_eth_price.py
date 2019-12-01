import requests
from django.core.cache import cache
from django.core.management.base import BaseCommand

URL = 'https://min-api.cryptocompare.com/data/price?fsym={from_symbol}&tsyms={to_symbol}'
CACHE_KEY = 'ETH-to-USD'


class Command(BaseCommand):
	help = 'Fetch price of ETH and stores to memcache'

	def add_arguments(self, parser):
		parser.add_argument('--from', type=str, default='ETH')
		parser.add_argument('--to', type=str, default='USD')

	def handle(self, *args, **options):
		response = requests.get(URL.format(from_symbol=options['from'], to_symbol=options['to']))
		data = response.json()
		cache.set(CACHE_KEY, data['USD'])
