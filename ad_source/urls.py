from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='landing_page'),
]
