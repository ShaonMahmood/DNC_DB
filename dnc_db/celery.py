from __future__ import absolute_import

import os
import sys
import raven
import celery

from raven.contrib.celery import register_signal, register_logger_signal


class Celery(celery.Celery):
    pass

    # def on_configure(self):
    #     client = raven.Client('https://d7af2998ad074c9388afe72abd98f955:7b9779f805f54961b259c7ae8e00ca74@sentry.io/649561')
    #
    #     # register a custom filter to filter out duplicate logs
    #     register_logger_signal(client)
    #
    #     # hook into the Celery error handler
    #     register_signal(client)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dnc_db.settings')

app = Celery('dnc_db')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings', namespace="CELERY")
app.autodiscover_tasks()