import logging
import random

import ethereum.utils
import sha3
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from djmoney.contrib.exchange.models import Rate
from rest_framework import (
    exceptions,
    mixins,
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from . import (
    authentication,
    filters,
    models,
    serializers,
    tasks,
    utils,
    web3_providers
)

logger = logging.getLogger(__name__)


class TaskViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.TaskSerializer
    filterset_class = filters.TaskFilter
    lookup_field = 'sku'

    def get_object(self):
        try:
            return super(TaskViewSet, self).get_object()
        except Http404:
            # Retry with ID fallback on public task
            queryset = self.filter_queryset(self.get_queryset())
            lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
            filter_kwargs = {
                'pk': self.kwargs[lookup_url_kwarg],
                'is_private': False,
            }
            obj = get_object_or_404(queryset, **filter_kwargs)
            # May raise a permission denied
            self.check_object_permissions(self.request, obj)
            return obj

    def get_queryset(self):
        if self.action == 'retrieve':  # Return all tasks on detail
            return models.Task.objects.all()
        qs = models.Task.objects.active_for_user(self.request.user)
        if self.action == 'list':  # Don't show private tasks on list
            qs = qs.filter(is_private=False)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = serializers.TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            obj: models.Task = self.get_object()
            if not obj.user == request.user:
                self.permission_denied(
                    request,
                    message='only owner can delete task',
                )
        return super(TaskViewSet, self).destroy(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path='answer',
            url_name='task_answer', serializer_class=serializers.AnswerSerializer)
    def answer(self, request, sku=None):
        try:
            task = models.Task.objects.get(sku=sku)
        except models.Task.DoesNotExist:
            raise exceptions.NotFound(f"Task sku {sku} wasn't found")
        for question in request.data['questions']:
            if question['id'] not in task.questions.values_list('id', flat=True):
                raise exceptions.NotFound(f"Question id {question['id']} wasn't found in task {sku}")
            for option in question['options']:
                if option['id'] not in task.questions.filter(id=question['id']).values_list('options', flat=True):
                    raise exceptions.NotFound(
                        f"Option id {option['id']} wasn't found for question {option['id']} in task {sku}"
                    )
        request.data.update({"task": task, "user": request.user})
        serializer = serializers.AnswerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(task=task, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDashboardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TaskDashboardSerializer
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = filters.TaskDashboardFilter

    def get_queryset(self):
        return models.Task.objects.dashboard(user=self.request.user)

    def get_permissions(self):
        if self.request.method == 'OPTIONS':
            return []
        return super(TaskDashboardViewSet, self).get_permissions()

    def check_object_permissions(self, request, obj: models.Task):
        if not request.user.is_superuser and not obj.user == request.user:
            self.permission_denied(request, message='user not a task owner')
        super(TaskDashboardViewSet, self).check_object_permissions(request, obj)

    @action(methods=['post'], detail=True, url_path='withdraw', url_name='withdraw')
    def withdraw(self, request, *args, **kwargs):
        instance: models.Task = self.get_object()
        self.check_object_permissions(request, instance)
        tasks.update_task_is_active_balance.delay(
            task_id=instance.id, should_be_active=False
        )
        return super(TaskDashboardViewSet, self).retrieve(request, *args, **kwargs)


class QuestionViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer


class OptionViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = models.Option.objects.all()
    serializer_class = serializers.OptionSerializer


class AnswerViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer


@method_decorator(csrf_exempt, name='dispatch')
class SubscribeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Subscribe.objects.all()
    serializer_class = serializers.SubscribeSerializer
    permission_classes = permissions.AllowAny,


class RateViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Rate.objects.all()
    serializer_class = serializers.RateSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = None


@api_view(['GET', 'POST'])
@permission_classes([])
def auth_view(request):
    """
    This view handle all authentication-related logic
    """
    response_data = {}
    if request.method == 'GET':
        # Obtain authentication information - `is_authenticated`, `username`, `nonce`
        response_data.update({'is_authenticated': request.user.is_authenticated})
        if request.user.is_authenticated:
            response_data.update({'username': request.user.username})
        else:
            nonce = ''.join(random.choice(settings.AUTH_NONCE_CHOICES) for _ in range(settings.AUTH_NONCE_LENGTH))
            response_data.update({'nonce': nonce})
            request.session['login_nonce'] = nonce
    elif request.method == 'POST':
        if settings.DEBUG:  # pragma: no cover
            # Allow username/password auth in debug mode
            if 'username' in request.data and 'password' in request.data:
                username = request.data['username']
                password = request.data['password']
                user = get_object_or_404(User, username=username)
                if user.check_password(password):
                    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                    response_data.update({'is_authenticated': request.user.is_authenticated})
                    response_data.update({'username': request.user.username})
                    return Response(data=response_data, status=status.HTTP_200_OK)

        # Authenticate user by signed `nonce` == `user_signature` and verify against `user_address`
        login_nonce = request.session.pop('login_nonce', None)
        if not login_nonce:
            return Response(
                data={"login_nonce": "Session id doesn't have a `login_nonce`"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            user_address = request.data.get('user_address')
            if not user_address:
                return Response(
                    data={"user_address": "Request doesn't have a `user_address`"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_signature = request.data.get('user_signature')
            if not user_signature:
                return Response(
                    data={"user_signature": "Request doesn't have a `user_signature`"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Start the sign-up process
            seed = "\x19Ethereum Signed Message:\n" + str(len(login_nonce)) + login_nonce
            buffered_hashed_msg = ethereum.utils.sha3(seed)
            vrs = utils.sig_to_vrs(user_signature)
            recovered_addr = '0x' + sha3.keccak_256(
                ethereum.utils.ecrecover_to_pub(buffered_hashed_msg, *vrs)
            ).hexdigest()[24:]
            if not recovered_addr == user_address:
                return Response(
                    data={"user_signature": "User signature doesn't match `user_address`"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user, created = User.objects.get_or_create(
                username=recovered_addr,
            )
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")

            response_data.update({'is_authenticated': request.user.is_authenticated})
            response_data.update({'username': request.user.username})
            response_data.update({'created': created})
    return Response(data=response_data, status=status.HTTP_200_OK)


class Logout(views.APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_403_FORBIDDEN)
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserTasks(views.APIView):
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *, contract_address: str):
        user_tasks = models.Task.objects.filter(user=request.user, contract_address=contract_address)
        serializer = serializers.TaskSerializer(instance=user_tasks, context={'request': request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RewardViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Reward.objects.all()

    def create(self, request, *args, **kwargs):
        task_sku = kwargs['task_sku']
        task = get_object_or_404(models.Task, sku=task_sku)
        with transaction.atomic():
            if request.user.id not in task.answers.values_list('user_id', flat=True):
                data = {"error": "User didn't answer the task"}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            for question in task.questions.all():
                if question.is_quiz:
                    correct_option = question.options.get(is_correct=True)
                    if not task.answers.filter(user=request.user, selected_options=correct_option).exists():
                        data = {"error": "User didn't answer the task correctly"}
                        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            reward, created = models.Reward.objects.get_or_create(
                receiver=request.user,
                task=task,
                defaults={
                    'sender': task.user,
                    'amount': task.reward_per_click.amount,
                }
            )
            if created:
                w3_provider: web3_providers.Web3Provider = web3_providers.web3_storage[task.chain]
                tx_hash = w3_provider.create_reward(task, reward)
                tasks.update_task_is_active_balance.delay(task_id=task.id, wait_for_tx=tx_hash)
                data = {
                    "tx_hash": tx_hash
                }
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                data = {
                    "error": "Reward already created"
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        logger.error(f"GET on /task/{kwargs.get('task_id')}/reward. {request.user}")
        return exceptions.bad_request(request, exception=None)


class ServerConfigViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        data = {
            'public_key': settings.ACCOUNT_OWNER_PUBLIC_KEY
        }
        return Response(data)
