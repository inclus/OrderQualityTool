# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facility',
            name='district',
            field=models.ForeignKey(related_name='facilities', blank=True, to='locations.District', null=True),
        ),
    ]
