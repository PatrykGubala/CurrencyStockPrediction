from typing import List, Optional
from myapp.repositories.currency_pairs_repository import CurrencyPairsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository

class CurrencyPairsService:
    def __init__(self):
        self.currency_pairs_repo = CurrencyPairsRepository()
        self.currencies_repo = CurrenciesRepository()
    def get_all_currency_pairs_dto(self) -> List[dict]:
        pairs = self.currency_pairs_repo.get_all_currency_pairs()
        result = []
        for p in pairs:
            result.append({
                "id": p.id,
                "base_currency": {"id": p.base_currency.id, "code": p.base_currency.code, "name": p.base_currency.name, "symbol": p.base_currency.symbol},
                "target_currency": {"id": p.target_currency.id, "code": p.target_currency.code, "name": p.target_currency.name, "symbol": p.target_currency.symbol}
            })
        return result
    def get_currency_pair_by_id_dto(self, pair_id: int) -> Optional[dict]:
        p = self.currency_pairs_repo.get_currency_pair_by_id(pair_id)
        if not p:
            return None
        return {
            "id": p.id,
            "base_currency": {"id": p.base_currency.id, "code": p.base_currency.code, "name": p.base_currency.name, "symbol": p.base_currency.symbol},
            "target_currency": {"id": p.target_currency.id, "code": p.target_currency.code, "name": p.target_currency.name, "symbol": p.target_currency.symbol}
        }
    def create_currency_pair(self, base_currency_code: str, target_currency_code: str) -> Optional[dict]:
        base_currency = self.currencies_repo.get_currency_by_code(base_currency_code)
        target_currency = self.currencies_repo.get_currency_by_code(target_currency_code)
        if not base_currency or not target_currency:
            return None
        existing_pair = self.currency_pairs_repo.get_currency_pair(base_currency.id, target_currency.id)
        if existing_pair:
            return {
                "id": existing_pair.id,
                "base_currency": {"id": base_currency.id, "code": base_currency.code, "name": base_currency.name, "symbol": base_currency.symbol},
                "target_currency": {"id": target_currency.id, "code": target_currency.code, "name": target_currency.name, "symbol": target_currency.symbol}
            }
        new_pair = self.currency_pairs_repo.add_currency_pair(base_currency.id, target_currency.id)
        return {
            "id": new_pair.id,
            "base_currency": {"id": new_pair.base_currency.id, "code": new_pair.base_currency.code, "name": new_pair.base_currency.name, "symbol": new_pair.base_currency.symbol},
            "target_currency": {"id": new_pair.target_currency.id, "code": new_pair.target_currency.code, "name": new_pair.target_currency.name, "symbol": new_pair.target_currency.symbol}
        }
    def delete_currency_pair(self, pair_id: int) -> bool:
        return self.currency_pairs_repo.delete_currency_pair(pair_id)
