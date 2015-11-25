# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '__first__'),
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
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
        ),
        migrations.CreateModel(
            name='AdultPatientsRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('existing', models.FloatField(null=True, blank=True)),
                ('new', models.FloatField(null=True, blank=True)),
                ('formulation', models.CharField(max_length=256, null=True, blank=True)),
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
                ('packs_ordered', models.FloatField(null=True, blank=True)),
                ('total_quantity_to_be_ordered', models.FloatField(null=True, blank=True)),
                ('notes', models.CharField(max_length=256, null=True, blank=True)),
                ('formulation', models.CharField(max_length=256, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FacilityCycleRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cycle', models.CharField(max_length=256)),
                ('reporting_status', models.BooleanField(default=False)),
                ('web_based', models.BooleanField(default=False)),
                ('multiple', models.BooleanField(default=False)),
                ('facility', models.ForeignKey(to='locations.Facility')),
            ],
        ),
        migrations.CreateModel(
            name='PAEDPatientsRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('existing', models.FloatField(null=True, blank=True)),
                ('new', models.FloatField(null=True, blank=True)),
                ('formulation', models.CharField(max_length=256, null=True, blank=True)),
                ('facility_cycle', models.ForeignKey(to='dashboard.FacilityCycleRecord')),
            ],
        ),
        migrations.AddField(
            model_name='facilityconsumptionrecord',
            name='facility_cycle',
            field=models.ForeignKey(to='dashboard.FacilityCycleRecord'),
        ),
        migrations.AddField(
            model_name='adultpatientsrecord',
            name='facility_cycle',
            field=models.ForeignKey(to='dashboard.FacilityCycleRecord'),
        ),
    ]
