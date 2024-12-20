import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Currency_Stock_Prediction_Django.settings')
app = Celery('Currency_Stock_Prediction_Django')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()