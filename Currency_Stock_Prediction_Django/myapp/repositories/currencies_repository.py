from typing import List, Optional
from myapp.models import Currency

class CurrenciesRepository:
    def get_currency_by_id(self, currency_id: int) -> Optional[Currency]:
        return Currency.objects.get(pk=currency_id)

    def get_currency_by_code(self, code: str) -> Optional[Currency]:
        return Currency.objects.filter(code=code).first()

    def get_all_currencies(self) -> List[Currency]:
        return list(Currency.objects.all())

    def add_currency(self, code: str, name: str, symbol: Optional[str] = None) -> Currency:
        currency = Currency(code=code, name=name, symbol=symbol)
        currency.save()
        return currency

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
