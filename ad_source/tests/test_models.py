import datetime

from django.test import testcases
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

from ad_source import models
from ad_source.tests import mixins


class TaskModelTestCase(mixins.DataTestMixin, testcases.TestCase):

    def test_create_task_with_currency_conversion(self):
        reward_per_click = Money(1, 'USD')
        remaining_balance = Money(10, 'USD')
        task = models.Task.objects.create(
            website_link="http://example.com",
            title="Example task",
            description="Awesome site. Go check",
            contract_address="0xdeadc0dedeadc0de",
            chain="goerli",
            og_image_link="https://via.placeholder.com/300x200.png",
            reward_per_click=reward_per_click,
            remaining_balance=remaining_balance,
            time_duration=datetime.timedelta(seconds=30),
            created="2013-01-01 00:00:00+00:00",
            modified="2013-01-01 00:00:00+00:00",
            user_id=1,
            is_active=True,
        )
        self.assertEqual(task.reward_per_click.currency.code, 'ETH')
        self.assertAlmostEqual(task.reward_per_click.amount, convert_money(reward_per_click, 'ETH').amount)

        self.assertEqual(task.remaining_balance.currency.code, 'ETH')
        self.assertAlmostEqual(task.remaining_balance.amount, convert_money(remaining_balance, 'ETH').amount)

        self.assertEqual(task.reward_usd_per_click.currency.code, 'USD')
        self.assertAlmostEqual(task.reward_usd_per_click.amount, reward_per_click.amount)

        self.assertEqual(task.remaining_balance_usd.currency.code, 'USD')
        self.assertAlmostEqual(task.remaining_balance_usd.amount, remaining_balance.amount)

    def test_create_task_without_currency_conversion(self):
        reward_per_click = Money(1, 'ETH')
        remaining_balance = Money(10, 'ETH')
        task = models.Task.objects.create(
            website_link="http://example.com",
            title="Example task",
            contract_address="0xdeadc0dedeadc0de",
            description="Awesome site. Go check",
            chain="goerli",
            og_image_link="https://via.placeholder.com/300x200.png",
            reward_per_click=reward_per_click,
            remaining_balance=remaining_balance,
            time_duration=datetime.timedelta(seconds=30),
            modified="2013-01-01 00:00:00+00:00",
            created="2013-01-01 00:00:00+00:00",
            is_active=True,
            user_id=1,
        )
        self.assertEqual(task.reward_per_click.currency.code, 'ETH')
        self.assertAlmostEqual(task.reward_per_click.amount, reward_per_click.amount)

        self.assertEqual(task.remaining_balance.currency.code, 'ETH')
        self.assertAlmostEqual(task.remaining_balance.amount, remaining_balance.amount)

        self.assertEqual(task.reward_usd_per_click.currency.code, 'USD')
        self.assertAlmostEqual(task.reward_usd_per_click.amount, convert_money(reward_per_click, 'USD').amount)

        self.assertEqual(task.remaining_balance_usd.currency.code, 'USD')
        self.assertAlmostEqual(task.remaining_balance_usd.amount, convert_money(remaining_balance, 'USD').amount)
