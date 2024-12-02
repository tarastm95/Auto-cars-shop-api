from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

app = Celery('currency')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-exchange-rates-every-day': {
        'task': 'apps.currency.tasks.fetch_exchange_rates',
        'schedule': crontab(minute=0, hour=0),
    },
}

app.conf.update(
    broker_url='redis://redis:6379/0',
    result_backend='redis://redis:6379/0',
)
