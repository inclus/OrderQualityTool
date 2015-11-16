# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_auto_20151116_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='art_consumption',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='closing_balance',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='estimated_number_of_new_patients',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='estimated_number_of_new_pregnant_women',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='loses_adjustments',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='months_of_stock_of_hand',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='opening_balance',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='pmtct_consumption',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='quantity_received',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='quantity_required_for_current_patients',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='facilityconsumptionrecord',
            name='total_quantity_to_be_ordered',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
