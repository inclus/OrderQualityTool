# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_remove_facilityconsumptionrecord_drug_formulation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adultpatientsrecord',
            name='drug_formulation',
        ),
        migrations.RemoveField(
            model_name='paedpatientsrecord',
            name='drug_formulation',
        ),
        migrations.AddField(
            model_name='adultpatientsrecord',
            name='formulation',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='paedpatientsrecord',
            name='formulation',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
