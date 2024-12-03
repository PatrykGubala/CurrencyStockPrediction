from typing import Optional, List
from app.models.models import CurrencyPair
from app.models.database import db

class CurrencyPairsRepository:
    def get_currency_pair_by_id(self, pair_id: int) -> Optional[CurrencyPair]:
        return CurrencyPair.query.get(pair_id)

    def get_currency_pair(self, base_currency_id: int, target_currency_id: int) -> Optional[CurrencyPair]:
        return CurrencyPair.query.filter_by(base_currency_id=base_currency_id, target_currency_id=target_currency_id).first()

    def get_all_currency_pairs(self) -> List[CurrencyPair]:
        return CurrencyPair.query.all()

    def add_currency_pair(self, base_currency_id: int, target_currency_id: int) -> CurrencyPair:
        pair = CurrencyPair(base_currency_id=base_currency_id, target_currency_id=target_currency_id)
        db.session.add(pair)
        db.session.commit()
        return pair

    def delete_currency_pair(self, pair_id: int) -> bool:
        pair = self.get_currency_pair_by_id(pair_id)
        if pair:
            db.session.delete(pair)
            db.session.commit()
            return True
        return False
