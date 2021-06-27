from django.conf import settings
from djmoney.contrib.exchange.backends.base import SimpleExchangeBackend


class CryptoCompareBackend(SimpleExchangeBackend):
    name = "cryptocompare.com"

    def __init__(self, url=settings.CRYPTOCOMPARE_URL):
        self.url = url

    def get_url(self, **params):
        return self.url.format(**params)

    def get_rates(self, **params):
        response = self.get_response(**params)
        return self.parse_json(response)[params['base_currency']]
