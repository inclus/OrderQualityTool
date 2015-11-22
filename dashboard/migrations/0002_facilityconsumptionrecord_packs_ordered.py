# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityconsumptionrecord',
            name='packs_ordered',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
