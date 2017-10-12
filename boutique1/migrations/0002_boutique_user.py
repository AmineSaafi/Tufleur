# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-31 12:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('boutique1', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='boutique',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
