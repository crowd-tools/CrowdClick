"""
Django settings for CrowdClick project.

`init` script for the settings module.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os
import sys

import environ
from split_settings.tools import optional, include

from .web3_config import Web3Config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env(
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG=(bool, True),

    ENV=(str, 'local'),

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY=(str, '39h^zm85$8ehrv+_1o=d-k9caiu_e=$)0oti42w9)krz4@6_0c'),
    ALLOWED_HOSTS=(list, ["*"]),

    DATABASE_URL=(str, f"sqlite://{os.path.join(BASE_DIR, '../db.sqlite3')}"),  # XXX DEFAULT_DATABASE_ENV?

    ACCOUNT_OWNER_PUBLIC_KEY=(str, '0x9c76e3A23A87f624aAdEff7ca5e74103476eD11C'),  # ServerConfigViewSet
    WEB3_CONFIG=(dict, {
        'mumbai': Web3Config()  # dataclass defaults
        # 'goerli', ...
    }),
    DJANGO_ADMIN_URL=(str, 'admin'),

    SENTRY_DSN=(str, ''),
)

# reading .env file
environ.Env.read_env()

DEBUG = env.bool('DEBUG')
SECRET_KEY = env.str('SECRET_KEY')

ENV = env.str('ENV')
TEST = ('test' in sys.argv) or ('unittest' in sys.argv) or os.getenv('CI')

ENV_PRODUCTION = 'production'
ENV_STAGING = 'staging'
ENV_DEVELOP = 'develop'  # reserved
ENV_LOCAL = 'local'

if ENV == ENV_PRODUCTION:
    ENVIRONMENT = ENV_PRODUCTION
elif ENV == ENV_STAGING:
    ENVIRONMENT = ENV_STAGING
else:
    ENVIRONMENT = ENV_LOCAL

print(f'Using environment: {ENVIRONMENT}: TEST: {TEST}', file=sys.stderr)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {'default': env.db('DATABASE_URL')}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SENTRY_DSN = env.str('SENTRY_DSN')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment=ENVIRONMENT,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,

        # Our current plan covers 10M transactions, our usage is ~30K per month
        traces_sample_rate=1.0,

        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )

env_settings = f'{ENVIRONMENT.lower()}.py'

include(
    'defaults.py',
    'crowdclick.py',
    optional('logging.py'),

    optional(env_settings if not TEST else None),
    optional('testing.py' if TEST else None),
    optional('local_optional.py' if not TEST else None),

    scope=locals()
)
