# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-07 00:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_auto_20151204_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilityCycleRecordScore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test', models.CharField(max_length=256)),
                ('score', models.CharField(choices=[(b'YES', b'YES'), (b'NO', b'NO'), (b'NOT_REPORTING', b'NOT_REPORTING')], db_index=True, max_length=20)),
                ('facility_cycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.FacilityCycleRecord')),
            ],
        ),
    ]
