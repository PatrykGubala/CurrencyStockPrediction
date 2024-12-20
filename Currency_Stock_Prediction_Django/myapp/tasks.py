from celery import shared_task
from myapp.services.currency_pairs_data_service import CurrencyPairsDataService

@shared_task
def load_currency_data_task(pair_ids=1, frequency='daily'):
    service = CurrencyPairsDataService()
    service.load_hourly_data(pair_ids)
    service.load_daily_data(pair_ids)


