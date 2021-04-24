import datetime
import decimal

import requests
from django.conf import settings
from django.core.cache import cache


class ETH2USD:
    BASE_URL = settings.ETH2USD_URL.format(from_symbol='ETH,BNB,MATIC', to_symbol='USD')

    @classmethod
    def get(cls, from_symbol='ETH', to_symbol='USD') -> decimal.Decimal:
        data = cache.get(settings.ETH2USD_CACHE_KEY, {}).get("data", {})
        value = data.get(from_symbol, {}).get(to_symbol, None)
        if not value:
            data = cls.set()
            value = data.get(from_symbol, {}).get(to_symbol, None)
        if value and isinstance(value, float):
            value = decimal.Decimal(str(value))
        return value

    @classmethod
    def get_dict(cls) -> dict:
        """
        :return: {'data': {'ETH': {'USD': 2206}, ..., 'MATIC': {'USD': 0.347}}, 'last_updated': datetime}
        """
        data = cache.get(settings.ETH2USD_CACHE_KEY, default={})
        if not data:
            cls.set()
            data = cache.get(settings.ETH2USD_CACHE_KEY, default={})
        return data

    @classmethod
    def set(cls, value: {} = None):
        if not value:
            value = cls.fetch()
        data = {
            "last_updated": datetime.datetime.now().isoformat(),
            "data": value
        }
        cache.set(settings.ETH2USD_CACHE_KEY, data)
        return value

    @classmethod
    def fetch(cls) -> dict:
        response = requests.get(cls.BASE_URL)
        return response.json()  # {'ETH': {'USD': 2206}, 'BNB': {'USD': 496.27}, 'MATIC': {'USD': 0.347}}
