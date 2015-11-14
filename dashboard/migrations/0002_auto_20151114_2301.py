# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dashboarduser',
            name='location',
            field=models.ForeignKey(blank=True, to='locations.Location', null=True),
        ),
    ]
