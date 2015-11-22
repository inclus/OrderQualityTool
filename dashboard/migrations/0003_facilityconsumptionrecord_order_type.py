# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_facilityconsumptionrecord_packs_ordered'),
    ]

    operations = [
        migrations.AddField(
            model_name='facilityconsumptionrecord',
            name='order_type',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
