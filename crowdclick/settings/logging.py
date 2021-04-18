from pathlib import Path
import typing

if typing.TYPE_CHECKING:
    from . import *

if ENVIRONMENT == ENV_PRODUCTION:
    LOG_ROOT = Path('/var/log/crowdclick')
elif ENVIRONMENT == ENV_STAGING:
    LOG_ROOT = Path('/var/log/crowdclick_stage')
elif ENVIRONMENT == ENV_DEVELOP:
    LOG_ROOT = Path('/var/log/crowdclick_dev')  # reserved
else:
    LOG_ROOT = BASE_DIR.parent.joinpath('logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': LOG_ROOT.joinpath('crowdclick.log'),
            'backupCount': 30,
            'when': 'midnight',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'DEBUG',
        },
        'requests': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False
        },
        'ad_source': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
        }
    }
}
