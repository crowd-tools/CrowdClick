import datetime
import unittest
from decimal import Decimal

from djmoney.contrib.exchange.models import Rate, ExchangeBackend
from djmoney.money import Money

from ad_source import models


class UserMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.admin = models.User.objects.create_superuser(
            username='admin',
            password='admin',
        )
        cls.user = models.User.objects.create_user(
            username='0xa1f765189805e0e51ac9753a9bc7d99e2b90c705',
            password='user'
        )


class TaskMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        models.Task.objects.create(
            website_link="http://example.com",
            title="Check our site",
            description="Awesome site. Go check",
            contract_address="0xdeadc0dedeadc0de",
            chain="goerli",
            og_image_link="https://via.placeholder.com/300x200.png",
            reward_per_click=Money(1, 'USD'),
            sku='GOEASK',  # Goerli task
            uuid='ada12a54-f21b-4d22-b598-89481f407c8c',
            # remaining_balance=Money(10, 'ETH'),
            time_duration=datetime.timedelta(seconds=30),
            created="2013-01-01 00:00:00+00:00",
            modified="2013-01-01 00:00:00+00:00",
            is_active=True,
            user_id=1
        )
        models.Task.objects.create(
            website_link="http://todo.com",
            title="Not active task",
            contract_address="0xdeadbeefdeadbeef",
            chain="mumbai",
            description="Not active task. Go check",
            reward_per_click=Money(1, 'MATIC'),
            # remaining_balance=Money(10, 'MATIC'),
            sku='MUMASK',  # Mumbai task
            uuid='7fa8d8d4-3e79-4427-9547-eea84a9af699',
            time_duration=datetime.timedelta(seconds=30),
            created="2013-01-01 00:00:00+00:00",
            modified="2013-01-01 00:00:00+00:00",
            user_id=2
        )
        models.Task.objects.create(
            website_link="http://example.com/survey",
            title="Survey task",
            contract_address="0xdeadbeefdeadbeef",
            chain="goerli",
            description="Survey task. Guess the correct answer",
            reward_per_click=Money(1, 'ETH'),
            sku='SURASK',  # Survey task
            uuid='f7098ff8-18b5-43f2-9123-83a815b250be',
            # remaining_balance=Money(10, 'ETH'),
            time_duration=datetime.timedelta(seconds=30),
            created="2013-01-01 00:00:00+00:00",
            modified="2013-01-01 00:00:00+00:00",
            user_id=1
        )


class QuestionMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        models.Question.objects.create(
            task_id=1,
            title="Was it good?",
            question_type="RA"
        )
        models.Question.objects.create(
            task_id=1,
            title="Was it fast?",
            question_type="RA"
        )
        models.Question.objects.create(
            task_id=3,
            title="To be or not to be?",
            question_type="RA"
        )


class OptionsMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        models.Option.objects.create(
            title="Good",
            question_id=1
        )
        models.Option.objects.create(
            title="Bad",
            question_id=1
        )
        models.Option.objects.create(
            title="Fast",
            question_id=2
        )
        models.Option.objects.create(
            title="Slow",
            question_id=2
        )
        models.Option.objects.create(
            title="To be",
            is_correct=True,
            question_id=3
        )
        models.Option.objects.create(
            title="Not to be",
            question_id=3
        )


class RateMixin(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        backend, _created = ExchangeBackend.objects.get_or_create(
            name='cryptocompare.com',
            defaults={
                'base_currency': 'USD',
            },
        )
        Rate.objects.create(
            currency='BNB',
            value=Decimal('0.003600'),
            backend=backend
        )
        Rate.objects.create(
            currency='ETH',
            value=Decimal('	0.000550'),
            backend=backend
        )
        Rate.objects.create(
            currency='MATIC',
            value=Decimal('0.956900'),
            backend=backend
        )


class DataTestMixin(UserMixin, TaskMixin, QuestionMixin, OptionsMixin, RateMixin):
    pass
