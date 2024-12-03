from typing import List, Optional
from app.models.models import Currency
from app.models.database import db

class CurrenciesRepository:
    def get_currency_by_code(self, code: str) -> Optional[Currency]:
        return Currency.query.filter_by(code=code).first()

    def get_all_currencies(self) -> List[Currency]:
        return Currency.query.all()

    def add_currency(self, code: str, name: str, symbol: Optional[str] = None) -> Currency:
        currency = Currency(code=code, name=name, symbol=symbol)
        db.session.add(currency)
        db.session.commit()
        return currency

    def update_currency(self, currency_id: int, new_name: str, new_symbol: Optional[str] = None) -> Optional[Currency]:
        currency = Currency.query.get(currency_id)
        if currency:
            currency.name = new_name
            currency.symbol = new_symbol
            db.session.commit()
        return currency

    def delete_currency(self, currency_id: int) -> bool:
        currency = Currency.query.get(currency_id)
        if currency:
            db.session.delete(currency)
            db.session.commit()
            return True
        return False