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
    'update-task-is-active-balance': {
        'task': 'ad_source.tasks.push_underlying_usd_price',
        'schedule': datetime.timedelta(hours=1),
        'options': {'expires': 60}
    }
}
