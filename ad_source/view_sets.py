import random

import ethereum.utils
import sha3
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from rest_framework import permissions, status
from rest_framework import viewsets, mixins
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from . import serializers, models, authentication, utils
from .models import Task


class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Task.objects.all()
    serializer_class = serializers.TaskSerializer

    @action(methods=['post'], detail=True, permission_classes=[permissions.IsAuthenticated],
            url_path='answer', url_name='task_answer', serializer_class=serializers.AnswerSerializer)
    def answer(self, request, pk=None):
        try:
            task_id = int(pk)
        except ValueError:
            return HttpResponseBadRequest(content=b'Task id %s is not a number' % pk.encode('utf-8'))
        try:
            task = Task.objects.get(pk=task_id)
        except ObjectDoesNotExist:
            return HttpResponseNotFound(content=b"Task id %d wasn't found" % task_id)
        for question in request.data['questions']:
            if question['id'] not in task.questions.values_list('id', flat=True):
                return HttpResponseNotFound(
                    content=b"Question id %d wasn't found in task %d" % (question['id'], task_id)
                )
            for option in question['options']:
                if option['id'] not in task.questions.filter(id=question['id']).values_list('options', flat=True):
                    return HttpResponseNotFound(
                        content=b"Option id %d wasn't found for question %d in task %d" % (
                            option['id'], question['id'], task_id
                        )
                    )
        request.data.update({"task": task, "user": request.user})
        serializer = serializers.AnswerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(task=task, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, permission_classes=[permissions.IsAuthenticated],
            url_path='dashboard', url_name='task_dashboard', serializer_class=serializers.TaskDashboardSerializer)
    def dashboard(self, request):
        tasks = models.Task.objects.dashboard(user=request.user)
        serializer = serializers.TaskDashboardSerializer(instance=tasks, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = serializers.TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = models.Question.objects.all()
    serializer_class = serializers.QuestionSerializer


class OptionViewSet(viewsets.ModelViewSet):
    queryset = models.Option.objects.all()
    serializer_class = serializers.OptionSerializer


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer


class SubscribeViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Subscribe.objects.all()
    serializer_class = serializers.SubscribeSerializer
    permission_classes = permissions.AllowAny,


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
            buffered_hashed_msg = ethereum.utils.sha3(login_nonce)
            vrs = utils.sig_to_vrs(user_signature)
            recovered_addr = '0x' + sha3.keccak_256(
                ethereum.utils.ecrecover_to_pub(buffered_hashed_msg, *vrs)
            ).hexdigest()[24:]
            if recovered_addr == user_address:
                user, created = User.objects.get_or_create(
                    username=recovered_addr,
                )
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                response_data.update({'is_authenticated': request.user.is_authenticated})
                response_data.update({'username': request.user.username})
                response_data.update({'created': created})
            else:
                return Response(
                    data={"user_signature": "User signature doesn't match `user_address`"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
    return Response(data=response_data, status=status.HTTP_200_OK)
