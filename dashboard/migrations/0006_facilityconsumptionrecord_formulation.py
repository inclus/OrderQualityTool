# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0005_auto_20151124_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityconsumptionrecord',
            name='formulation',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
