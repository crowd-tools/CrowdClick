from django.urls import path, include
from rest_framework import routers

from . import views, view_sets

router = routers.DefaultRouter()
router.register(r'ads', view_sets.AdvertisementViewSet)
router.register(r'question', view_sets.QuestionViewSet)

urlpatterns = [
    path('', views.home, name='landing_page'),
    path('logout', views.logout, name='logout'),
    path('advertisement', views.advertisement, name="advertisement"),
    path('earn/<int:ad_id>', views.earn, name="earn"),
    path('about', views.about, name='about'),
    path('publish', views.publish, name='publish'),
    path('api/', include(router.urls)),
]
