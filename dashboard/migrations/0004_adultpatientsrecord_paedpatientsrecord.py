# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0003_facilityconsumptionrecord_order_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdultPatientsRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('existing', models.FloatField(null=True, blank=True)),
                ('new', models.FloatField(null=True, blank=True)),
                ('drug_formulation', models.ForeignKey(to='dashboard.DrugFormulation')),
                ('facility_cycle', models.ForeignKey(to='dashboard.FacilityCycleRecord')),
            ],
        ),
        migrations.CreateModel(
            name='PAEDPatientsRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('existing', models.FloatField(null=True, blank=True)),
                ('new', models.FloatField(null=True, blank=True)),
                ('drug_formulation', models.ForeignKey(to='dashboard.DrugFormulation')),
                ('facility_cycle', models.ForeignKey(to='dashboard.FacilityCycleRecord')),
            ],
        ),
    ]
