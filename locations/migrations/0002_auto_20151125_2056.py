# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='level',
        ),
        migrations.RemoveField(
            model_name='location',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='location',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='location',
            name='tree_id',
        ),
        migrations.AlterField(
            model_name='location',
            name='parent',
            field=models.ForeignKey(related_name='children', blank=True, to='locations.Location', null=True),
        ),
    ]
