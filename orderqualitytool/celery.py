from __future__ import absolute_import

import os

from celery import Celery
from raven import Client
from raven.contrib.celery import register_signal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orderqualitytool.settings")

from django.conf import settings

app = Celery("orderqualitytool")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


if hasattr(settings, "RAVEN_CONFIG"):
    # Celery signal registration
    dsn = settings.RAVEN_CONFIG["dsn"]
    if dsn:
        client = Client(dsn=dsn)
        register_signal(client)
