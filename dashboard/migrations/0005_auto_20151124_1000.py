# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_adultpatientsrecord_paedpatientsrecord'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facilityconsumptionrecord',
            name='order_type',
        ),
        migrations.AddField(
            model_name='facilitycyclerecord',
            name='order_type',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='facilitycyclerecord',
            name='reporting',
            field=models.CharField(max_length=60, null=True, blank=True),
        ),
    ]
