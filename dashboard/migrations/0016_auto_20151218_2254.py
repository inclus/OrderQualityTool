# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-18 19:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0015_auto_20151218_0556'),
    ]

    operations = [
        migrations.AddField(
            model_name='score',
            name='fail_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='score',
            name='pass_count',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
