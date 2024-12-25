from decimal import Decimal

from celery import shared_task
from django.utils import timezone

from myapp.models.models import AccountCurrencyValueHistory
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.services.accounts_service import AccountsService
from myapp.services.currencies_data_service import CurrenciesDataService

@shared_task
def load_currency_data_task(pair_ids=1, frequency='daily'):
    service = CurrenciesDataService()
    service.load_hourly_data(pair_ids)
    service.load_daily_data(pair_ids)


@shared_task
def recount_currency_values():
    service = AccountsService()
    service.recount_currency_values()