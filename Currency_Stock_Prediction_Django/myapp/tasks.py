from datetime import timedelta
from decimal import Decimal

from celery import shared_task
from django.utils import timezone

from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.services.accounts_service import AccountsService
from myapp.services.companies_service import CompaniesService
from myapp.services.currencies_data_service import CurrenciesDataService, logger
from myapp.services.currencies_trained_models_service import CurrenciesTrainedModelsService
from myapp.services.exchanges_service import ExchangesService
from myapp.services.stocks_data_service import StocksDataService
from myapp.services.stocks_recommendations_service import StockRecommendationsService
from myapp.services.stocks_service import StocksService
from myapp.utils.finnhub_loader_service import FinnhubLoaderService


@shared_task
def load_currency_data_task(*args, **kwargs):
    logger.info("10 MINUT 10 MINUT 10 MINUT 10 MINUT 10 MINUT 10 MINUT 10 MINUT 10 MINUT.")

    service = CurrenciesDataService()
    currencies_to_load = ['EUR','GBP' ,'PLN' ,'JPY' ,'CNY' ,'AUD' ,'CHF' ,'NOK' ,'INR' ,'AUD' , 'SEK' ,'NZD' ,'MXN']
    now = timezone.now()
    last_31_days = now - timedelta(days=31)

    for currency_code in currencies_to_load:
        latest_ts = service.repository.get_latest_timestamp_for_currency_code(currency_code)
        if not latest_ts:
            service.load_daily_data_for_range(currency_code, start_date="2012-01-01", end_date=last_31_days)
            service.load_hourly_data_for_range(currency_code, start_date=last_31_days, end_date=now)
        else:
            if latest_ts < last_31_days:
                service.load_daily_data_for_range(currency_code, start_date=latest_ts, end_date=last_31_days)
                service.load_hourly_data_for_range(currency_code, start_date=last_31_days, end_date=now)
            else:
                service.load_hourly_data_for_range(currency_code, start_date=latest_ts, end_date=now)







@shared_task
def load_stocks_data_task():
    service = StocksDataService()
    stocks_to_load = ['AAPL', 'TSLA', 'MSFT']
    now = timezone.now()
    last_31_days = now - timedelta(days=31)
    for symbol in stocks_to_load:
        stock = service.repository.get_stock_by_symbol(symbol)
        if stock:
            latest_ts = service.repository.get_latest_timestamp_for_stock(stock)
            if not latest_ts:
                service.load_daily_data_for_range(symbol, start_date="2012-01-01", end_date=last_31_days)
                service.load_hourly_data_for_range(symbol, start_date=last_31_days, end_date=now)
            else:
                if latest_ts < last_31_days:
                    service.load_daily_data_for_range(symbol, start_date=latest_ts, end_date=last_31_days)
                    service.load_hourly_data_for_range(symbol,start_date=last_31_days, end_date=now)
                else:
                    service.load_hourly_data_for_range(symbol, start_date=latest_ts, end_date=now)






@shared_task
def recount_currency_values():
    service = AccountsService()
    service.recount_currency_values()






@shared_task
def train_usdpln_model_async():
    service = CurrenciesTrainedModelsService()
    result = service.train_model_for_currency(currency_code="PLN", model_name="SeasonalRNN")
    return result





