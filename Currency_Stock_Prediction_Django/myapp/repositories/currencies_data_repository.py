from datetime import datetime
from typing import Optional, List

import logging
from django.db.models import Max
from django.db.models.functions import TruncDate

from myapp.models import Currency, CurrenciesData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrenciesDataRepository:
    def get_currency_by_id(self, currency_id: int) -> Optional[Currency]:
        return Currency.objects.filter(pk=currency_id).first()

    def get_currency_by_code(self, currency_code: str) -> Optional[Currency]:
        return Currency.objects.filter(code=currency_code).first()

    def bulk_upsert_data(self, currency: Currency, data: List[dict]):
        objs = []
        for record in data:
            objs.append(CurrenciesData(
                currency=currency,
                timestamp=record['timestamp'],
                open_price=record['open_price'],
                high_price=record['high_price'],
                low_price=record['low_price'],
                close_price=record['close_price'],
                volume=record['volume']
            ))
        CurrenciesData.objects.bulk_create(objs, ignore_conflicts=True)
        logger.info(f"Successfully upserted {len(objs)} records for {currency.code}")

    def get_latest_timestamp_for_currency(self, currency: Currency) -> Optional[datetime]:
        result = CurrenciesData.objects.filter(currency=currency).aggregate(latest=Max('timestamp'))
        return result['latest']

    def get_latest_record(self, currency: Currency) -> Optional[CurrenciesData]:
        return CurrenciesData.objects.filter(currency=currency).order_by('-timestamp').first()

    def get_previous_record(self, currency: Currency, current_timestamp: datetime) -> Optional[CurrenciesData]:
        return CurrenciesData.objects.filter(
            currency=currency,
            timestamp__lt=current_timestamp
        ).order_by('-timestamp').first()

    def get_all_data(self) -> List[dict]:
        result = []
        for data in CurrenciesData.objects.select_related('currency').order_by('-id'):
            result.append({
                'currency_id': data.currency.id,
                'timestamp': data.timestamp,
                'open': str(data.open_price),
                'high': str(data.high_price),
                'low': str(data.low_price),
                'close': str(data.close_price),
                'volume': str(data.volume)
            })
        return result

    def get_data(self, currency: Currency, frequency: str, start_date: datetime, end_date: datetime) -> Optional[
        List[CurrenciesData]]:
        return list(
            CurrenciesData.objects.filter(
                currency=currency,
                timestamp__range=(start_date, end_date)
            ).order_by('timestamp')
        )

    def get_data_raw(self, currency: Currency, frequency: str, start_date: Optional[datetime], end_date: datetime):
        queryset = CurrenciesData.objects.filter(currency=currency)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        else:
            queryset = queryset.filter(timestamp__lte=end_date)
        if frequency == "daily":
            queryset = queryset.annotate(date=TruncDate('timestamp'))
        return queryset

    def get_latest_timestamp_for_currency_code(self, currency_code: str) -> Optional[datetime]:
        currency = Currency.objects.filter(code=currency_code).first()
        if not currency:
            return None
        result = CurrenciesData.objects.filter(currency=currency).aggregate(latest=Max('timestamp'))
        return result['latest']