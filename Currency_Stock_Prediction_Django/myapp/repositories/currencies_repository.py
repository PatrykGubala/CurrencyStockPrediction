from typing import List, Optional
from myapp.models import Currency, CurrenciesData, Region, Country


class CurrenciesRepository:
    def get_currency_by_id(self, currency_id: int) -> Optional[Currency]:
        return Currency.objects.get(pk=currency_id)

    def get_currency_by_code(self, code: str) -> Optional[Currency]:
        return Currency.objects.filter(code=code).first()

    def get_all_currencies(self) -> List[Currency]:
        return list(Currency.objects.all())

    def get_available_currencies(self) -> List[Currency]:
        return list(Currency.objects.filter(data_availability=True))

    def add_currency(self, code: str, name: str, symbol: Optional[str] = None) -> Currency:
        currency = Currency(code=code, name=name, symbol=symbol)
        currency.save()
        return currency

    def get_currencies_by_region(self, region_name: str) -> List[Currency]:
        try:
            region = Region.objects.get(region_name=region_name)
            countries = Country.objects.filter(regions=region)
            return list(Currency.objects.filter(countries__in=countries, data_availability=True).distinct())
        except Region.DoesNotExist:
            return []

    def update_currency(self, currency_id: int, new_name: str, new_symbol: Optional[str] = None) -> Optional[Currency]:
        try:
            currency = Currency.objects.get(pk=currency_id)
            currency.name = new_name
            currency.symbol = new_symbol
            currency.save()
            return currency
        except Currency.DoesNotExist:
            return None

    def delete_currency(self, currency_id: int) -> bool:
        try:
            currency = Currency.objects.get(pk=currency_id)
            currency.delete()
            return True
        except Currency.DoesNotExist:
            return False

    def get_latest_currency_data(self, currency_code: str) -> Optional[CurrenciesData]:
        return CurrenciesData.objects.filter(currency__code=currency_code).order_by('-timestamp').first()