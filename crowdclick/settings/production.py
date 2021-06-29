import datetime
import os

DEBUG = False

CELERY_TASK_DEFAULT_QUEUE = 'crowdclick_celery'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "backend_static"),
]

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = ['rest_framework.renderers.JSONRenderer']


CELERY_BEAT_SCHEDULE = {
    'update_rates': {
        'task': 'ad_source.tasks.update_rates',
        'schedule': datetime.timedelta(minutes=10),
        'options': {'expires': 600},
    },
}
