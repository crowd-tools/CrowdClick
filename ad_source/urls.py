from django.conf import settings
from django.urls import path, include
from rest_framework import routers

from . import view_sets

if settings.DEBUG:
    router_class = routers.DefaultRouter
else:
    router_class = routers.SimpleRouter

router = router_class()
router.register(r'task/dashboard', view_sets.TaskDashboardViewSet,  basename='task_dashboard')
router.register(r'task', view_sets.TaskViewSet,  basename='task_view')
router.register(r'task/(?P<task_sku>\w+)/reward', view_sets.RewardViewSet, basename='reward_view')
router.register(r'answer', view_sets.AnswerViewSet)
router.register(r'question', view_sets.QuestionViewSet)
router.register(r'option', view_sets.OptionViewSet)
router.register(r'subscribe', view_sets.SubscribeViewSet)
router.register(r'rates', view_sets.RateViewSet, basename='rates')
router.register(r'server_config', view_sets.ServerConfigViewSet, basename='server_config')


urlpatterns = [
    path('api/', include(router.urls)),
    path(r'api/auth/', view_sets.auth_view, name='auth_view'),
    path(r'api/auth/logout/', view_sets.Logout.as_view(), name='logout_view'),
    path(r'api/user/tasks/<str:contract_address>/', view_sets.UserTasks.as_view(), name='user_tasks_view')
]
