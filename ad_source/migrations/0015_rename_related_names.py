# Generated by Django 2.2.13 on 2020-07-10 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ad_source', '0014_move_temp_answer_to_answer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='selected_options',
            field=models.ManyToManyField(related_name='answers', to='ad_source.Option'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answers', to='ad_source.Task'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='answers', to=settings.AUTH_USER_MODEL),
        ),
    ]
