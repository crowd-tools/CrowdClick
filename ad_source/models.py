import datetime
from decimal import Decimal as D

from django.contrib.auth.models import User
from django.core import validators
from django.db import models

from . import helpers, managers


class Task(models.Model):
    GOERLI = 'goerli'
    MUMBAI = 'mumbai'
    BINANCE_TESTNET = 'bsc_testnet'
    BINANCE_MAINNET = 'bsc_mainnet'
    CHAIN_CHOICES = (
        (GOERLI, 'Goerli'),
        (MUMBAI, 'Mumbai'),
        (BINANCE_TESTNET, 'bsc_testnet'),
        (BINANCE_MAINNET, 'bsc_mainnet'),
    )

    title = models.CharField("Title", max_length=100)
    description = models.TextField("Description", max_length=100)
    chain = models.CharField("Chain", max_length=15, choices=CHAIN_CHOICES, default=GOERLI)
    uuid = models.UUIDField('Web3 Task Identifier', unique=True, null=True)
    website_link = models.CharField("Website Link", max_length=200, validators=[validators.URLValidator])
    website_image = models.ImageField("Website Image", upload_to="task_website_image", null=True)
    contract_address = models.CharField("Contract address", max_length=42)
    reward_per_click = models.DecimalField("Reward per click", max_digits=9, decimal_places=3)  # ETH but shown as USD
    og_image_link = models.URLField("OpenGraph Image Path", max_length=200, blank=True, null=True)
    time_duration = models.DurationField("Time duration", default=datetime.timedelta(seconds=30))
    created = models.DateTimeField("Created", auto_now_add=True)  # No show
    modified = models.DateTimeField("Modified", auto_now=True)  # No show
    is_active = models.BooleanField("Is active", default=True)
    is_active_web3 = models.BooleanField("Is active on Web3", default=True)
    remaining_balance = models.DecimalField(
        "Remaining balance for task", max_digits=9, decimal_places=3, null=True, default=None)  # ETH but shown as USD
    initial_budget = models.DecimalField('Initial task budget ', max_digits=9, decimal_places=3, null=True, default=None) #ETH but shown as USD
    user = models.ForeignKey(User, related_name='tasks', on_delete=models.DO_NOTHING)
    warning_message = models.CharField("Warning message", max_length=100, blank=True)

    objects = managers.TaskManager()

    class Meta:
        verbose_name_plural = "Task"

    def __str__(self):  # pragma: no cover
        if self.title:
            return f"Task({self.title})"
        return "Task"

    @property
    def reward_usd_per_click(self):
        eth_to_usd = helpers.ETH2USD.get()
        return self.reward_per_click * D(str(eth_to_usd))

    @property
    def remaining_balance_usd(self):
        eth_to_usd = helpers.ETH2USD.get()
        return self.remaining_balance * D(str(eth_to_usd))


class Question(models.Model):
    RADIO_TYPE = 'RA'
    SELECT_TYPE = 'SE'
    QUESTION_TYPES = (
        (RADIO_TYPE, 'Radio'),
        (SELECT_TYPE, 'Select'),
    )

    task = models.ForeignKey(Task, related_name="questions", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES, default=SELECT_TYPE)

    objects = managers.QuestionManager()

    class Meta:
        verbose_name_plural = "   Question"

    def __str__(self):  # pragma: no cover
        return f"Question({self.title})"


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
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
