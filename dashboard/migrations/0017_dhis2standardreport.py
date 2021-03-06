# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-11-07 02:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("dashboard", "0016_auto_20171030_0222")]

    operations = [
        migrations.CreateModel(
            name="Dhis2StandardReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(db_index=True, max_length=256)),
                ("report_id", models.CharField(db_index=True, max_length=256)),
                (
                    "partner",
                    models.CharField(
                        choices=[
                            (b"MAUS", b"MAUS"), (b"JMS", b"JMS"), (b"NMS", b"NMS")
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "report_type",
                    models.CharField(
                        choices=[
                            (b"Consumption Data Report", b"Consumption Data Report"),
                            (
                                b"Adult/PMTCT ART Patient Report",
                                b"Adult/PMTCT ART Patient Report",
                            ),
                        ],
                        max_length=50,
                    ),
                ),
                ("org_unit_id", models.CharField(db_index=True, max_length=20)),
            ],
        )
    ]
