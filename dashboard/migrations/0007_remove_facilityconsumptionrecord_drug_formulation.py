# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_facilityconsumptionrecord_formulation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facilityconsumptionrecord',
            name='drug_formulation',
        ),
    ]
