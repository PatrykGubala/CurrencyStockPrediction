from typing import List, Optional
from myapp.repositories.currencies_repository import CurrenciesRepository

class CurrenciesService:
    def __init__(self):
        self.currencies_repo = CurrenciesRepository()

    def get_all_currencies_dto(self) -> List[dict]:
        currencies = self.currencies_repo.get_all_currencies()
        return [{"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol} for currency in currencies]

    def get_currency_by_id_dto(self, currency_id: int) -> Optional[dict]:
        currency = self.currencies_repo.get_currency_by_id(currency_id)
        if not currency:
            return None
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}

    def get_currency_by_code_dto(self, code: str) -> Optional[dict]:
        currency = self.currencies_repo.get_currency_by_code(code)
        if not currency:
            return None
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}

    def add_currency(self, code: str, name: str, symbol: Optional[str] = None) -> dict:
        existing = self.currencies_repo.get_currency_by_code(code)
        if not existing:
            currency = self.currencies_repo.add_currency(code, name, symbol)
        else:
            currency = existing
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}

    def update_currency(self, currency_id: int, new_name: str, new_symbol: Optional[str] = None) -> Optional[dict]:
        currency = self.currencies_repo.update_currency(currency_id, new_name, new_symbol)
        if not currency:
            return None
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol}

    def delete_currency(self, currency_id: int) -> bool:
        return self.currencies_repo.delete_currency(currency_id)
