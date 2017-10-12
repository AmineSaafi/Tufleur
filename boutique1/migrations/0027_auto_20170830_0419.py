# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-30 04:19
from __future__ import unicode_literals

import boutique1.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boutique1', '0026_auto_20170829_2302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 709711)),
        ),
        migrations.AlterField(
            model_name='collection',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 706683)),
        ),
        migrations.AlterField(
            model_name='pic',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 710632)),
        ),
        migrations.AlterField(
            model_name='pic',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=boutique1.models.user_directory_path_seven),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 708486)),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='end_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 708556)),
        ),
        migrations.AlterField(
            model_name='promotion',
            name='start_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 708529)),
        ),
        migrations.AlterField(
            model_name='shop',
            name='create_date',
            field=models.DateTimeField(default=datetime.datetime(2017, 8, 30, 4, 19, 46, 703298)),
        ),
    ]
