# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0004_auto_20151109_1610'),
        ('dashboard', '0002_auto_20151114_2301'),
    ]

    operations = [
        migrations.CreateModel(
            name='DrugFormulation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('unit', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='FacilityConsumptionRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opening_balance', models.IntegerField()),
                ('quantity_received', models.IntegerField()),
                ('pmtct_consumption', models.IntegerField()),
                ('art_consumption', models.IntegerField()),
                ('loses_adjustments', models.IntegerField()),
                ('closing_balance', models.IntegerField()),
                ('months_of_stock_of_hand', models.IntegerField()),
                ('quantity_required_for_current_patients', models.IntegerField()),
                ('estimated_number_of_new_patients', models.IntegerField()),
                ('estimated_number_of_new_pregnant_women', models.IntegerField()),
                ('total_quantity_to_be_ordered', models.IntegerField()),
                ('notes', models.CharField(max_length=256)),
                ('drug_formulation', models.ForeignKey(to='dashboard.DrugFormulation')),
            ],
        ),
        migrations.CreateModel(
            name='FacilityCycleRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cycle', models.CharField(max_length=256)),
                ('facility', models.ForeignKey(to='locations.Location')),
            ],
        ),
        migrations.AddField(
            model_name='facilityconsumptionrecord',
            name='facility_cycle',
            field=models.ForeignKey(to='dashboard.FacilityCycleRecord'),
        ),
    ]
