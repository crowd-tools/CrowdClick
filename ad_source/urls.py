from django.urls import path, include
from rest_framework import routers

from . import views, view_sets

router = routers.DefaultRouter()
router.register(r'task', view_sets.TaskViewSet)
router.register(r'question', view_sets.QuestionViewSet)

urlpatterns = [
    path('', views.home, name='landing_page'),
    path('logout', views.logout, name='logout'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('task', views.task, name="task"),
    path('advertising_matrix', views.advertising_matrix, name="advertising_matrix"),
    path('earn/<int:ad_id>', views.earn, name="earn"),
    path('about', views.about, name='about'),
    path('publish', views.publish, name='publish'),
    path('api/', include(router.urls)),
]
