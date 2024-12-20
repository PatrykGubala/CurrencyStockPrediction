from datetime import datetime
from typing import Optional, List
from myapp.models import CurrencyPair, CurrencyPairData
import logging
from django.db.models import Max

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrencyPairsDataRepository:
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

    def bulk_upsert_data(self, pair: CurrencyPair, data: List[dict]):
        objs = []
        for record in data:
            objs.append(CurrencyPairData(
                currency_pair=pair,
                timestamp=record['timestamp'],
                open_price=record['open_price'],
                high_price=record['high_price'],
                low_price=record['low_price'],
                close_price=record['close_price'],
                volume=record['volume']
            ))
        CurrencyPairData.objects.bulk_create(objs, ignore_conflicts=True)
        logger.info(f"Successfully upserted {len(objs)} records for {pair.name}")

    def get_latest_timestamp_for_pair(self, pair: CurrencyPair) -> Optional[datetime]:
        result = CurrencyPairData.objects.filter(currency_pair=pair).aggregate(latest=Max('timestamp'))
        return result['latest']

    def get_latest_record(self, pair: CurrencyPair) -> Optional[CurrencyPairData]:
        return CurrencyPairData.objects.filter(currency_pair=pair).order_by('-timestamp').first()

    def get_previous_record(self, pair: CurrencyPair, current_timestamp: datetime) -> Optional[CurrencyPairData]:
        return CurrencyPairData.objects.filter(
            currency_pair=pair,
            timestamp__lt=current_timestamp
        ).order_by('-timestamp').first()