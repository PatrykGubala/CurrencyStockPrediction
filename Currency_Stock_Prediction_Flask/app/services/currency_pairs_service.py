from typing import List, Optional
from app.repositories.currency_pairs_repository import CurrencyPairsRepository
from app.repositories.currencies_repository import CurrenciesRepository
from app.models.dtos import CurrencyPairDTO
from app.utils.logger import setup_logger

class CurrencyPairsService:
    def __init__(self):
        self.currency_pairs_repo = CurrencyPairsRepository()
        self.currencies_repo = CurrenciesRepository()
        self.logger = setup_logger(__name__)

    def get_all_currency_pairs_dto(self) -> List[CurrencyPairDTO]:
        currency_pairs = self.currency_pairs_repo.get_all_currency_pairs()
        currency_pairs_dto = []
        for pair in currency_pairs:
            pair_dict: CurrencyPairDTO = {
                "id": pair.id,
                "base_currency": {
                    "id": pair.base_currency.id,
                    "code": pair.base_currency.code,
                    "name": pair.base_currency.name,
                    "symbol": pair.base_currency.symbol
                },
                "target_currency": {
                    "id": pair.target_currency.id,
                    "code": pair.target_currency.code,
                    "name": pair.target_currency.name,
                    "symbol": pair.target_currency.symbol
                }
            }
            currency_pairs_dto.append(pair_dict)
        return currency_pairs_dto

    def get_currency_pair_by_id_dto(self, pair_id: int) -> Optional[CurrencyPairDTO]:
        pair = self.currency_pairs_repo.get_currency_pair_by_id(pair_id)
        if not pair:
            return None
        pair_dto: CurrencyPairDTO = {
            "id": pair.id,
            "base_currency": {
                "id": pair.base_currency.id,
                "code": pair.base_currency.code,
                "name": pair.base_currency.name,
                "symbol": pair.base_currency.symbol
            },
            "target_currency": {
                "id": pair.target_currency.id,
                "code": pair.target_currency.code,
                "name": pair.target_currency.name,
                "symbol": pair.target_currency.symbol
            }
        }
        return pair_dto

    def create_currency_pair(self, base_currency_code: str, target_currency_code: str) -> Optional[CurrencyPairDTO]:
        try:
            self.logger.info(f"Tworzenie pary walutowej: {base_currency_code}/{target_currency_code}")
            base_currency = self.currencies_repo.get_currency_by_code(base_currency_code)
            target_currency = self.currencies_repo.get_currency_by_code(target_currency_code)
            if not base_currency or not target_currency:
                self.logger.error("Jedna z walut nie została znaleziona.")
                return None

            existing_pair = self.currency_pairs_repo.get_currency_pair(base_currency.id, target_currency.id)
            if existing_pair:
                self.logger.warning(f"Para walutowa {base_currency_code}/{target_currency_code} już istnieje.")
                return {
                    "id": existing_pair.id,
                    "base_currency": {
                        "id": base_currency.id,
                        "code": base_currency.code,
                        "name": base_currency.name,
                        "symbol": base_currency.symbol
                    },
                    "target_currency": {
                        "id": target_currency.id,
                        "code": target_currency.code,
                        "name": target_currency.name,
                        "symbol": target_currency.symbol
                    }
                }

            new_pair = self.currency_pairs_repo.add_currency_pair(base_currency.id, target_currency.id)
            pair_dto: CurrencyPairDTO = {
                "id": new_pair.id,
                "base_currency": {
                    "id": new_pair.base_currency.id,
                    "code": new_pair.base_currency.code,
                    "name": new_pair.base_currency.name,
                    "symbol": new_pair.base_currency.symbol
                },
                "target_currency": {
                    "id": new_pair.target_currency.id,
                    "code": new_pair.target_currency.code,
                    "name": new_pair.target_currency.name,
                    "symbol": new_pair.target_currency.symbol
                }
            }
            self.logger.info(f"Para walutowa {base_currency_code}/{target_currency_code} została utworzona pomyślnie.")
            return pair_dto
        except Exception as e:
            self.logger.error(f"Błąd podczas tworzenia pary walutowej: {e}")
            raise

    def delete_currency_pair(self, pair_id: int) -> bool:
        try:
            self.logger.info(f"Usuwanie pary walutowej ID {pair_id}")
            result = self.currency_pairs_repo.delete_currency_pair(pair_id)
            if result:
                self.logger.info(f"Para walutowa ID {pair_id} została usunięta pomyślnie.")
            else:
                self.logger.warning(f"Para walutowa ID {pair_id} nie została znaleziona.")
            return result
        except Exception as e:
            self.logger.error(f"Błąd podczas usuwania pary walutowej ID {pair_id}: {e}")
            raise