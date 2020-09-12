from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from . import view_sets

if settings.DEBUG:
    router_class = routers.DefaultRouter
else:
    router_class = routers.SimpleRouter

router = router_class()
router.register(r'task', view_sets.TaskViewSet,  basename='task_view')
router.register(r'task/(?P<task_id>\d+)/answer', view_sets.TaskViewSet)
router.register(r'answer', view_sets.AnswerViewSet)
router.register(r'question', view_sets.QuestionViewSet)
router.register(r'option', view_sets.OptionViewSet)
router.register(r'subscribe', view_sets.SubscribeViewSet)
router.register(r'prices/eth', view_sets.ETHMemCacheViewSet, basename='eth_view')


urlpatterns = [
    path('api/', include(router.urls)),
    path(r'api/auth/', view_sets.auth_view, name='auth_view'),
    path(r'api/reward/<int:task_id>', view_sets.reward_for_task, name='reward_view'),
    path(r'api/auth/logout/', view_sets.Logout.as_view(), name='logout_view'),
]
