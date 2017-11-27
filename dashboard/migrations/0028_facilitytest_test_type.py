# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-11-27 00:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_auto_20171127_0255'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilitytest',
            name='test_type',
            field=models.CharField(choices=[(b'FACILITY_ONLY', b'FACILITY_ONLY'), (b'FACILITY_AND_SAMPLE_FORMULATION', b'FACILITY_AND_SAMPLE_FORMULATION')], default='FACILITY_ONLY', max_length=255),
            preserve_default=False,
        ),
    ]
