import os

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdclick.settings')

app = Celery('crowdclick')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

if settings.SENTRY_DSN_CELERY:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN_CELERY,
        integrations=[CeleryIntegration()],
        environment=settings.ENVIRONMENT,

        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production,

        # Our current plan covers 10M transactions, our usage is ~30K per month
        traces_sample_rate=1.0,
    )
