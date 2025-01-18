from datetime import datetime
from typing import List, Optional
from django.db.models import Max, Sum
from django.db.models.functions import TruncDate
from myapp.models import Stock, StocksData

class StocksDataRepository:
    def bulk_upsert_data(self, stock: Stock, data: List[dict]):
        objs = []
        for record in data:
            objs.append(
                StocksData(
                    stock=stock,
                    timestamp=record['timestamp'],
                    open_price=record['open_price'],
                    high_price=record['high_price'],
                    low_price=record['low_price'],
                    close_price=record['close_price'],
                    volume=record['volume']
                )
            )
        StocksData.objects.bulk_create(objs, ignore_conflicts=True)

    def get_stock_by_symbol(self, stock_symbol: str) -> Optional[Stock]:
        return Stock.objects.filter(stock_symbol__iexact=stock_symbol).first()

    def get_latest_timestamp_for_stock(self, stock: Stock) -> Optional[datetime]:
        result = StocksData.objects.filter(stock=stock).aggregate(latest=Max('timestamp'))
        return result['latest']

    def get_latest_record(self, stock: Stock) -> Optional[StocksData]:
        return StocksData.objects.filter(stock=stock).order_by('-timestamp').first()

    def get_previous_record(self, stock: Stock, reference_ts: datetime) -> Optional[StocksData]:
        return StocksData.objects.filter(stock=stock, timestamp__lt=reference_ts).order_by('-timestamp').first()

    def get_data_raw(self, stock: Stock, start_date: Optional[datetime], end_date: datetime):
        queryset = StocksData.objects.filter(stock=stock)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        else:
            queryset = queryset.filter(timestamp__lte=end_date)
        return queryset.order_by('timestamp')

    def get_all_data(self) -> List[dict]:
        result = []
        for data in StocksData.objects.select_related('stock').order_by('-id'):
            result.append({
                'stock_symbol': data.stock.stock_symbol,
                'timestamp': data.timestamp.isoformat(),
                'open_price': str(data.open_price),
                'high_price': str(data.high_price),
                'low_price': str(data.low_price),
                'close_price': str(data.close_price),
                'volume': str(data.volume)
            })
        return result
