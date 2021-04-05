import logging

from django.core.cache import cache
from django.core.management.base import BaseCommand

from ad_source.helpers import ETH2USD_CACHE_KEY

Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = f"Print content of memcache['{ETH2USD_CACHE_KEY}'] to stdout"

    def handle(self, *args, **options):
        Logger.warning(cache.get(ETH2USD_CACHE_KEY))
