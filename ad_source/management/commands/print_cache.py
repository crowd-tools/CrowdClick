import logging

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand

Logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = f"Print content of memcache['{settings.ETH2USD_CACHE_KEY}'] to stdout"

    def handle(self, *args, **options):
        Logger.warning(cache.get(settings.ETH2USD_CACHE_KEY))
