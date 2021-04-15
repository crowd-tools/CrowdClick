from pathlib import Path


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
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # TODO config `ADMINS`, `EMAIL_SUBJECT_PREFIX`, SERVER_EMAIL. See django.core.mail.mail_admins
        # 'mail_admins': {
        #     'level': 'ERROR',
        #     'class': 'django.utils.log.AdminEmailHandler',
        #     'filters': ['special']
        # }
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOG_ROOT.joinpath('crowdclick.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        # 'django.request': {
        #     'handlers': ['mail_admins'],
        #     'level': 'ERROR',
        #     'propagate': False,
        # },
        'ad_source': {
            'handlers': ['file', ],
            'level': 'INFO',
        }
    }
}
