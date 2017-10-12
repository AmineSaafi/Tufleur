# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-04 14:12
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boutique1', '0012_auto_20170804_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 4, 15, 12, 58, 739075)),
        ),
        migrations.AddField(
            model_name='shop',
            name='processing_time',
            field=models.FloatField(default=0),
        ),
    ]
