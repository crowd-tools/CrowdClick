# Generated by Django 3.2.6 on 2021-08-24 18:12

import uuid

from django.db import migrations, models


def generate_task_sku(apps, schema_editor):
    Task = apps.get_model('ad_source', 'Task')

    def _generate_sku():
        while True:
            sku = uuid.uuid4().hex[:6].upper()
            if not Task.objects.filter(sku=sku).exists():
                break
        return sku

    for task in Task.objects.all():
        task.sku = _generate_sku()
        task.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ad_source', '0029_auto_20210807_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_private',
            field=models.BooleanField(default=False, verbose_name='Is private'),
        ),
        migrations.AddField(
            model_name='task',
            name='sku',
            field=models.CharField(blank=True, null=True, max_length=6, verbose_name='SKU'),
        ),
        migrations.RunPython(code=generate_task_sku, reverse_code=migrations.RunPython.noop),
    ]
