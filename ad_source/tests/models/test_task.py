import responses
from django.contrib.auth.models import User
from django.test import TestCase
from decimal import Decimal as D

from ad_source.models import Task


class TestTaskModel(TestCase):
    fixtures = ['0000_users']

    def setUp(self) -> None:
        self.admin_user = User.objects.get(username="admin")

    @responses.activate
    def test_save_two_tasks_with_second_missing_og_data_is_none(self):
        default_task_kwargs = {
            'title': 'Foo Bar',
            'description': 'This is Foo Bar',
            'reward_per_click': D("1.2"),
            'spend_daily': D("0.1"),
            'user': self.admin_user,
        }
        responses.add(**{
            'method': responses.GET,
            'url': 'http://foo.bar/',
            'body': '''
<!DOCTYPE html>
<html>
  <head>
    <meta property="og:image" content="http://ogp.me/logo.png">
  </head>
  <body></body>
</html>
                    ''',
            'status': 200,
            'content_type': 'text/html',
        })
        responses.add(**{
            'method': responses.GET,
            'url': 'http://fizz.bazz/',
            'body': '''
<!DOCTYPE html>
<html>
  <head></head>
  <body></body>
</html>
                    ''',
            'status': 200,
            'content_type': 'text/html',
        })
        first_task = Task.objects.create(
            **default_task_kwargs,
            website_link='http://foo.bar/',
        )
        second_task = Task.objects.create(
            **default_task_kwargs,
            website_link='http://fizz.bazz/',
        )
        self.assertEqual(first_task.og_image_link, "http://ogp.me/logo.png")
        self.assertEqual(second_task.og_image_link, None)
