# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilitycyclerecord',
            name='facility',
            field=models.ForeignKey(related_name='records', to='locations.Facility'),
        ),
    ]
