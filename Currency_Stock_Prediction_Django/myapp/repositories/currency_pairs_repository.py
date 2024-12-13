from typing import Optional, List
from myapp.models import CurrencyPair

class CurrencyPairsRepository:
    def get_currency_pair_by_id(self, pair_id: int) -> Optional[CurrencyPair]:
        try:
            return CurrencyPair.objects.get(pk=pair_id)
        except CurrencyPair.DoesNotExist:
            return None
    def get_currency_pair(self, base_currency_id: int, target_currency_id: int) -> Optional[CurrencyPair]:
        return CurrencyPair.objects.filter(base_currency_id=base_currency_id, target_currency_id=target_currency_id).first()
    def get_all_currency_pairs(self) -> List[CurrencyPair]:
        return list(CurrencyPair.objects.all())
    def add_currency_pair(self, base_currency_id: int, target_currency_id: int) -> CurrencyPair:
        currency_pair = CurrencyPair(base_currency_id=base_currency_id, target_currency_id=target_currency_id)
        currency_pair.save()
        return currency_pair
    def delete_currency_pair(self, pair_id: int) -> bool:
        currency_pair = self.get_currency_pair_by_id(pair_id)
        if currency_pair:
            currency_pair.delete()
            return True
        return False
