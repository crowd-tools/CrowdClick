# Generated by Django 2.2.13 on 2021-03-19 19:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ad_source', '0018_task_contract_address'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='spend_daily',
        ),
    ]
