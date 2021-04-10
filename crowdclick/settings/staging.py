import os

DEBUG = False

CELERY_DEFAULT_QUEUE = 'crowdclick_celery_stage'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "backend_static"),
]
