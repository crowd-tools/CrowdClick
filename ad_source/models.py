import datetime
import typing

from django.conf import settings
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from djmoney.contrib.exchange.models import convert_money
from djmoney.models.fields import CurrencyField
from djmoney.money import Money

from . import fields, managers

if typing.TYPE_CHECKING:
    from crowdclick.settings import Web3Config


class Task(models.Model):
    GOERLI = 'goerli'
    MUMBAI = 'mumbai'
    BINANCE_TESTNET = 'bsc_testnet'
    BINANCE_MAINNET = 'bsc_mainnet'
    CHAIN_CHOICES = (
        (GOERLI, 'Goerli (ETH)'),
        (MUMBAI, 'Mumbai (MATIC)'),
        (BINANCE_TESTNET, 'bsc_testnet (BNB)'),
        (BINANCE_MAINNET, 'bsc_mainnet (BNB)'),
    )

    title = models.CharField("Title", max_length=100)
    description = models.TextField("Description", max_length=100)
    chain = models.CharField("Chain", max_length=15, choices=CHAIN_CHOICES, default=GOERLI)
    uuid = models.UUIDField('Web3 Task Identifier', unique=True, null=True)
    website_link = models.CharField("Website Link", max_length=200, validators=[validators.URLValidator])
    website_image = models.ImageField("Website Image", upload_to="task_website_image", null=True)
    contract_address = models.CharField("Contract address", max_length=42)
    og_image_link = models.URLField("OpenGraph Image Path", max_length=200, blank=True, null=True)
    time_duration = models.DurationField("Time duration", default=datetime.timedelta(seconds=30))
    created = models.DateTimeField("Created", auto_now_add=True)  # No show
    modified = models.DateTimeField("Modified", auto_now=True)  # No show
    # XXX: rename `is_active` to `is_enabled`
    is_active = models.BooleanField("Is active", default=True)  # Read-only on API, manageable by admin
    is_active_web3 = models.BooleanField("Is active on Web3", default=True)  # Is active on Web 3
    initial_tx_hash = models.CharField("Initial transaction hash", max_length=66, blank=True, default='')
    user = models.ForeignKey(User, related_name='tasks', on_delete=models.DO_NOTHING)
    warning_message = models.CharField("Warning message", max_length=100, blank=True)

    currency = CurrencyField(
        choices=settings.CURRENCY_CHOICES,
        default=None,
        editable=False,
        max_length=5,
        null=True
    )
    reward_per_click = fields.MoneyField(
        "Reward per click",
        max_digits=18,
        decimal_places=10,
        default_currency=None,
        currency_field_name='currency'
    )
    remaining_balance = fields.MoneyField(
        "Remaining balance for task",
        max_digits=18,
        decimal_places=10,
        null=True,
        default=None,
        currency_field_name='currency'
    )
    initial_budget = fields.MoneyField(
        "Initial task budget",
        max_digits=18,
        decimal_places=10,
        null=True,
        default=None,
        currency_field_name='currency'
    )

    objects = managers.TaskManager()

    class Meta:
        verbose_name_plural = "Task"

    def __str__(self):  # pragma: no cover
        if self.title:
            return f"Task({self.title})"
        return "Task"

    def save(self, *args, **kwargs):
        if not self.currency or self.currency == 'USD':
            self.currency = self.chain_instance.currency
            for field in (
                'reward_per_click',
                'remaining_balance',
                'initial_budget',
            ):
                if getattr(self, field, False):
                    value = Money(getattr(self, field).amount, 'USD')
                    setattr(self, field, convert_money(value, self.chain_instance.currency))
        return super(Task, self).save(*args, **kwargs)

    @property
    def chain_instance(self) -> 'Web3Config':
        if self.chain in settings.WEB3_CONFIG:
            return settings.WEB3_CONFIG[self.chain]
        else:
            raise ImproperlyConfigured(f'{self.chain} not found in {list(settings.WEB3_CONFIG.keys())}')

    @property
    def reward_usd_per_click(self):
        return convert_money(self.reward_per_click, 'USD')

    @property
    def remaining_balance_usd(self):
        return convert_money(self.remaining_balance, 'USD')


class Question(models.Model):
    RADIO_TYPE = 'RA'
    SELECT_TYPE = 'SE'
    QUESTION_TYPES = (
        (RADIO_TYPE, 'Radio'),
        (SELECT_TYPE, 'Select'),
    )

    task = models.ForeignKey(Task, related_name="questions", on_delete=models.CASCADE)
    title = models.TextField()
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default=SELECT_TYPE)

    objects = managers.QuestionManager()

    class Meta:
        verbose_name_plural = "   Question"

    def __str__(self):  # pragma: no cover
        return f"Question({self.title})"


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    title = models.TextField()
    is_correct = models.BooleanField(default=False)

    objects = managers.OptionManager()

    class Meta:
        verbose_name_plural = "  Option"

    def __str__(self):  # pragma: no cover
        return f"Option({self.title})"


class Answer(models.Model):
    user = models.ForeignKey(User, related_name='answers', on_delete=models.PROTECT)
    task = models.ForeignKey(Task, related_name='answers', on_delete=models.PROTECT)
    selected_options = models.ManyToManyField(Option, related_name='answers')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = " Answer"

    def __str__(self):  # pragma: no cover
        return f'Answer({self.task}, user={self.user})'

    def answered_questions(self):
        return Question.objects.filter(
            id__in=self.selected_options.values_list('question', flat=True)
        )


class Reward(models.Model):
    sender = models.ForeignKey(User, related_name='send_rewards', on_delete=models.PROTECT)
    receiver = models.ForeignKey(User, related_name='received_rewards', on_delete=models.PROTECT)
    task = models.ForeignKey(Task, related_name='rewards', on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=27, decimal_places=18)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('receiver', 'task')


class Subscribe(models.Model):
    email = models.EmailField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
