# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_auto_20151124_1115'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DrugFormulation',
        ),
    ]
