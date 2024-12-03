from typing import List, Optional
from app.repositories.currencies_repository import CurrenciesRepository
from app.models.dtos import CurrencyDTO
from app.utils.logger import setup_logger

class CurrenciesService:
    def __init__(self):
        self.currencies_repo = CurrenciesRepository()
        self.logger = setup_logger(__name__)

    def get_all_currencies_dto(self) -> List[CurrencyDTO]:
        currencies = self.currencies_repo.get_all_currencies()
        currencies_dto = []
        for currency in currencies:
            currency_dict: CurrencyDTO = {
                "id": currency.id,
                "code": currency.code,
                "name": currency.name,
                "symbol": currency.symbol
            }
            currencies_dto.append(currency_dict)
        return currencies_dto

    def get_currency_by_id_dto(self, currency_id: int) -> Optional[CurrencyDTO]:
        currency = self.currencies_repo.get_currency_by_id(currency_id)
        if not currency:
            return None
        currency_dto: CurrencyDTO = {
            "id": currency.id,
            "code": currency.code,
            "name": currency.name,
            "symbol": currency.symbol
        }
        return currency_dto

    def get_currency_by_code_dto(self, code: str) -> Optional[CurrencyDTO]:
        currency = self.currencies_repo.get_currency_by_code(code)
        if not currency:
            return None
        currency_dto: CurrencyDTO = {
            "id": currency.id,
            "code": currency.code,
            "name": currency.name,
            "symbol": currency.symbol
        }
        return currency_dto

    def add_currency(self, code: str, name: str, symbol: Optional[str] = None) -> CurrencyDTO:
        try:
            self.logger.info(f"Adding currency: {code}")
            existing_currency = self.currencies_repo.get_currency_by_code(code)
            if not existing_currency:
                currency = self.currencies_repo.add_currency(code, name, symbol)
                self.logger.info(f"Currency {code} added successfully.")
            else:
                currency = existing_currency
                self.logger.info(f"Currency {code} already exists.")
            currency_dto: CurrencyDTO = {
                "id": currency.id,
                "code": currency.code,
                "name": currency.name,
                "symbol": currency.symbol
            }
            return currency_dto
        except Exception as e:
            self.logger.error(f"Error adding currency {code}: {e}")
            raise

    def update_currency(self, currency_id: int, new_name: str, new_symbol: Optional[str] = None) -> Optional[CurrencyDTO]:
        try:
            self.logger.info(f"Updating currency ID {currency_id} to new name: {new_name} and new symbol: {new_symbol}")
            currency = self.currencies_repo.update_currency(currency_id, new_name, new_symbol)
            if not currency:
                self.logger.warning(f"Currency with ID {currency_id} not found.")
                return None
            currency_dto: CurrencyDTO = {
                "id": currency.id,
                "code": currency.code,
                "name": currency.name,
                "symbol": currency.symbol
            }
            return currency_dto
        except Exception as e:
            self.logger.error(f"Error updating currency ID {currency_id}: {e}")
            raise

    def delete_currency(self, currency_id: int) -> bool:
        try:
            self.logger.info(f"Deleting currency ID {currency_id}")
            result = self.currencies_repo.delete_currency(currency_id)
            if result:
                self.logger.info(f"Currency ID {currency_id} deleted successfully.")
            else:
                self.logger.warning(f"Currency ID {currency_id} not found.")
            return result
        except Exception as e:
            self.logger.error(f"Error deleting currency ID {currency_id}: {e}")
            raise