# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_auto_20151116_0148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='notes',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
