"""crowdclick URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="CrowdClick API",
      default_version='v1',
      terms_of_service="https://github.com/crowd-tools/CrowdClick#readme",
      contact=openapi.Contact(email="www.bagr@gmail.com"),
      license=openapi.License(name="BSD-3 License"),
   ),
   public=True,
   permission_classes=(permissions.IsAuthenticated,),
)


def trigger_error(request):
    raise ZeroDivisionError("Keep calm and divide by zero - (This is emulated error)")


urlpatterns = [
    path(f'{settings.DJANGO_ADMIN_URL}/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('', include('ad_source.urls')),
    path('api/sentry-debug/', trigger_error),
] + static(
    settings.STATIC_URL, document_root=settings.STATIC_ROOT
) + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
