# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_auto_20151125_2056'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='org_level',
            new_name='level',
        ),
    ]
