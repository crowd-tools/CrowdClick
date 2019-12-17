from django.urls import path, include
from rest_framework import routers
from web3auth import urls as web3auth_urls

from . import view_sets

router = routers.DefaultRouter()
router.register(r'task', view_sets.TaskViewSet)
router.register(r'question', view_sets.QuestionViewSet)
router.register(r'option', view_sets.OptionViewSet)
router.register(r'subscribe', view_sets.SubscribeViewSet)


urlpatterns = [
    path('api/', include(router.urls)),
    path('', include(web3auth_urls)),
]
