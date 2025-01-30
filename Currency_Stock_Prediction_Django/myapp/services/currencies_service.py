from typing import List, Optional, Tuple

from myapp.apps import logger
from myapp.models import Region, Country, Currency
from myapp.repositories.currencies_data_repository import CurrenciesDataRepository
from myapp.repositories.currencies_repository import CurrenciesRepository

class CurrenciesService:
    def __init__(self):
        self.currencies_repository = CurrenciesRepository()
        self.currencies_data_repository = CurrenciesDataRepository()

    def get_all_currencies_dto(self) -> List[dict]:
        currencies = self.currencies_repository.get_available_currencies()
        return [{"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol, "data_availability": currency.data_availability} for currency in currencies]

    def get_currency_by_id_dto(self, currency_id: int) -> Optional[dict]:
        currency = self.currencies_repository.get_currency_by_id(currency_id)
        if not currency:
            return None
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol, "data_availability": currency.data_availability}

    def get_currency_by_code_dto(self, code: str) -> Optional[dict]:
        currency = self.currencies_repository.get_currency_by_code(code)
        if not currency:
            return None
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol, "data_availability": currency.data_availability}

    def add_currency(self, code: str, name: str, symbol: Optional[str] = None) -> dict:
        existing = self.currencies_repository.get_currency_by_code(code)
        if not existing:
            currency = self.currencies_repository.add_currency(code, name, symbol)
        else:
            currency = existing
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol, "data_availability": currency.data_availability}

    def update_currency(self, currency_id: int, new_name: str, new_symbol: Optional[str] = None) -> Optional[dict]:
        currency = self.currencies_repository.update_currency(currency_id, new_name, new_symbol)
        if not currency:
            return None
        return {"id": currency.id, "code": currency.code, "name": currency.name, "symbol": currency.symbol, "data_availability": currency.data_availability}

    def delete_currency(self, currency_id: int) -> bool:
        return self.currencies_repository.delete_currency(currency_id)

    def get_currencies_by_region(self, region_name):
        try:
            region = Region.objects.get(region_name=region_name)
            countries = Country.objects.filter(regions=region)
            currencies = Currency.objects.filter(countries__in=countries).distinct()
            return [self.currency_to_dto(currency) for currency in currencies]
        except Region.DoesNotExist:
            return []

    def currency_to_dto(self, currency):
        return {
            "id": currency.id,
            "code": currency.code,
            "name": currency.name,
            "symbol": currency.symbol,
            "dataAvailability": currency.data_availability
        }

    def convert_currency(self, amount: float, from_currency_code: str, to_currency_code: str) -> Tuple[
        Optional[float], Optional[float]]:
        try:
            from_currency = self.currencies_repository.get_currency_by_code(from_currency_code.upper())
            to_currency = self.currencies_repository.get_currency_by_code(to_currency_code.upper())

            if not from_currency or not to_currency:
                logger.warning(f"One or both currency codes not found: {from_currency_code}, {to_currency_code}")
                return None, None

            if not from_currency.data_availability or not to_currency.data_availability:
                logger.warning(
                    f"Data not available for one or both currencies: {from_currency_code}, {to_currency_code}")
                return None, None

            from_close_data = self.currencies_data_repository.get_latest_record(from_currency)
            to_close_data = self.currencies_data_repository.get_latest_record(to_currency)

            if not from_close_data or not to_close_data:
                logger.warning(
                    f"Latest data not available for one or both currencies: {from_currency_code}, {to_currency_code}")
                return None, None

            from_close = float(from_close_data.close_price)
            to_close = float(to_close_data.close_price)

            if from_close == 0:
                logger.warning(f"From currency close price is zero: {from_currency_code}")
                return None, None

            conversion_rate = to_close / from_close
            converted_amount = amount * conversion_rate

            logger.info(
                f"Converted {amount} {from_currency_code} to {converted_amount} {to_currency_code} at rate {conversion_rate}")

            return round(converted_amount, 2), round(conversion_rate, 6)

        except Exception as e:
            logger.error(f"Error in convert_currency: {e}")
            return None, None