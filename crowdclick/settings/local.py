"""
settings for local environment
"""

import datetime
import sys
import typing

if typing.TYPE_CHECKING:
    from crowdclick.settings import Web3Config


ALLOWED_HOSTS = ['*']

if 'INSTALLED_APPS' in locals():
    INSTALLED_APPS += [
        # 'debug_toolbar',  # `pip install django-debug-toolbar`
        # 'django_extensions',  # `pip install django-extensions`
    ]


class CorsMiddleware:
    """
    Adds CORS headers to response
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = 'true'
        response["Access-Control-Allow-Headers"] = 'content-type'
        return response


if 'MIDDLEWARE' in locals():
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'crowdclick.settings.local.CorsMiddleware',

        'django.contrib.auth.middleware.RemoteUserMiddleware',
    ]
if 'AUTHENTICATION_BACKENDS' in locals():
    AUTHENTICATION_BACKENDS += [
        'django.contrib.auth.backends.RemoteUserBackend',
    ]


