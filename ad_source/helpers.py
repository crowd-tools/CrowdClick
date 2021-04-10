import datetime
import decimal

import requests
from django.core.cache import cache

ETH2USD_URL = 'https://min-api.cryptocompare.com/data/price?fsym={from_symbol}&tsyms={to_symbol}'
ETH2USD_CACHE_KEY = 'ETH-PRICES'


class ETH2USD:
    @classmethod
    def get(cls, default: decimal.Decimal = None) -> decimal.Decimal:
        data = cache.get(ETH2USD_CACHE_KEY, {})
        value = data.get("USD", None)
        if not value:
            value = cls.set(value=default)
        return value

    @classmethod
    def get_dict(cls) -> dict:
        """
        :return: dict({"USD": Decimal('2099.65'), "last_updated": datetime})
        """
        data = cache.get(ETH2USD_CACHE_KEY)
        return data

    @classmethod
    def set(cls, value=None):
        if not value:
            url = ETH2USD_URL.format(from_symbol='ETH', to_symbol='USD')
            response = requests.get(url)
            data = response.json()  # {'USD': 2099.65}
            value = decimal.Decimal(str(data['USD']))
        data = {
            "last_updated": datetime.datetime.now().isoformat(),
            "USD": value
        }
        cache.set(ETH2USD_CACHE_KEY, data)
        return value
