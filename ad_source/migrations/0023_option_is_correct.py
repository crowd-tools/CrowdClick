# Generated by Django 2.2.18 on 2021-04-10 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ad_source', '0022_task_website_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='is_correct',
            field=models.BooleanField(default=False),
        ),
    ]