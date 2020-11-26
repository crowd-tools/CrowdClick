import random

import ethereum.utils
import sha3
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404
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
from web3 import Web3

from . import authentication, filters, models, serializers, utils, web3_providers
from .management.commands.fetch_eth_price import CACHE_KEY
from .models import Task

web3_storage = web3_providers.Web3ProviderStorage()


class TaskViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Task.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = serializers.TaskSerializer
    filterset_class = filters.TaskFilter

    @action(methods=['post'], detail=True, url_path='answer',
            url_name='task_answer', serializer_class=serializers.AnswerSerializer)
    def answer(self, request, pk=None):
        try:
            task_id = int(pk)
        except ValueError:
            raise exceptions.ValidationError(f"Task id {pk} is not a number")
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            raise exceptions.NotFound(f"Task id {task_id} wasn't found")
        for question in request.data['questions']:
            if question['id'] not in task.questions.values_list('id', flat=True):
                raise exceptions.NotFound(f"Question id {question['id']} wasn't found in task {task_id}")
            for option in question['options']:
                if option['id'] not in task.questions.filter(id=question['id']).values_list('options', flat=True):
                    raise exceptions.NotFound(
                        f"Option id {option['id']} wasn't found for question {option['id']} in task {task_id}"
                    )
        request.data.update({"task": task, "user": request.user})
        serializer = serializers.AnswerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(task=task, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = serializers.TaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDashboardViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.TaskDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = filters.TaskFilter

    def get_queryset(self):
        return models.Task.objects.dashboard(user=self.request.user)


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


class ETHMemCacheViewSet(mixins.ListModelMixin, viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        cache_dict = cache.get(CACHE_KEY, {})
        return Response(cache_dict)


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
        if settings.DEBUG:
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
            seed = "\x19Ethereum Signed Message:\n" + str(len((login_nonce))) + login_nonce
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

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        serializer = serializers.TaskSerializer(instance=tasks, context={'request': request}, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class RewardViewSet(viewsets.ModelViewSet):
    authentication_classes = [authentication.CsrfExemptSessionAuthentication, BasicAuthentication]
    queryset = models.Reward.objects.all()

    def create(self, request, *args, **kwargs):
        task_id = kwargs['task_id']
        task = get_object_or_404(models.Task, pk=task_id)
        reward, created = models.Reward.objects.get_or_create(
            receiver=request.user,
            task=task,
            defaults={
                'sender': task.user,
                'amount': task.reward_per_click,
            }
        )
        if created:
            checksummed_sender = Web3.toChecksumAddress(reward.sender.username)
            checksummed_receiver = Web3.toChecksumAddress(reward.receiver.username)

            w3_provider: web3_providers.Web3Provider = web3_storage[task.chain]
            transaction = w3_provider.contract.functions.forwardRewards(
                checksummed_receiver,  # To
                checksummed_sender,  # From
                task.website_link  # task's website url
            ).buildTransaction({
                'chainId': w3_provider.chain_id,
                'gas': w3_provider.default_gas_fee,
                'gasPrice': w3_provider.web3.toWei('1', 'gwei'),
                'nonce': w3_provider.web3.eth.getTransactionCount(w3_provider.public_key)
            })
            txn_signed = w3_provider.web3.eth.account.sign_transaction(transaction, private_key=w3_provider.private_key)
            tx_hash_hex = w3_provider.web3.eth.sendRawTransaction(txn_signed.rawTransaction)  # tx_hash
            tx_hash = tx_hash_hex.hex()
            data = {
                "tx_hash": tx_hash
            }
            return Response(data=data, status=status.HTTP_201_CREATED)
        else:
            data = {
                "error": "Reward already created"
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class ServerConfigViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    def list(self, request, *args, **kwargs):
        data = {
            'public_key': settings.ACCOUNT_OWNER_PUBLIC_KEY
        }
        return Response(data)
