from django.urls import path, include
from rest_framework import routers

from . import views, view_sets

router = routers.DefaultRouter()
router.register(r'ads', view_sets.AdvertisementViewSet)
router.register(r'question', view_sets.QuestionViewSet)

urlpatterns = [
    path('', views.home, name='landing_page'),
    path('about', views.about, name='about'),
    path('api/', include(router.urls)),
]
