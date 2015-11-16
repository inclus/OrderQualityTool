# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(null=True, verbose_name='last login', blank=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(unique=True, max_length=255, verbose_name='email address', db_index=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', verbose_name='groups')),
                ('location', models.ForeignKey(blank=True, to='locations.Location', null=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
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
                ('opening_balance', models.FloatField(null=True, blank=True)),
                ('quantity_received', models.FloatField(null=True, blank=True)),
                ('pmtct_consumption', models.FloatField(null=True, blank=True)),
                ('art_consumption', models.FloatField(null=True, blank=True)),
                ('loses_adjustments', models.FloatField(null=True, blank=True)),
                ('closing_balance', models.FloatField(null=True, blank=True)),
                ('months_of_stock_of_hand', models.FloatField(null=True, blank=True)),
                ('quantity_required_for_current_patients', models.FloatField(null=True, blank=True)),
                ('estimated_number_of_new_patients', models.FloatField(null=True, blank=True)),
                ('estimated_number_of_new_pregnant_women', models.FloatField(null=True, blank=True)),
                ('total_quantity_to_be_ordered', models.FloatField(null=True, blank=True)),
                ('notes', models.CharField(max_length=256, null=True, blank=True)),
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
