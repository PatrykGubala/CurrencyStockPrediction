import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Currency_Stock_Prediction_Django.settings')
app = Celery('Currency_Stock_Prediction_Django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'recount_currency_values_hourly': {
        'task': 'myapp.tasks.recount_currency_values',
        'schedule': crontab(minute='*/10'), },
}