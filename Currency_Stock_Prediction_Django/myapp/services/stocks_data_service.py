from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from django.utils import timezone
from typing import List, Optional
from django.db.models import Min, Max, Sum
from django.db.models.functions import TruncDate
from myapp.repositories.stocks_data_repository import StocksDataRepository

class StocksDataService:
    def __init__(self):
        self.repository = StocksDataRepository()

    def fetch_data(self, stock_symbol: str, frequency: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        try:
            ticker = yf.Ticker(stock_symbol)
            data_history = ticker.history(start=start_date, end=end_date, interval=frequency)
            if data_history.empty:
                return None
            data_history = data_history.reset_index()
            if 'Datetime' in data_history.columns:
                data_history['Datetime'] = pd.to_datetime(data_history['Datetime'], utc=True)
            elif 'Date' in data_history.columns:
                data_history['Date'] = pd.to_datetime(data_history['Date'], utc=True)
            return data_history
        except:
            return None

    def process_data(self, data_records: pd.DataFrame, daily: bool) -> List[dict]:
        if 'Date' in data_records.columns:
            data_records = data_records.rename(columns={'Date': 'timestamp'})
        elif 'Datetime' in data_records.columns:
            data_records = data_records.rename(columns={'Datetime': 'timestamp'})
        data_records = data_records.dropna(subset=['timestamp'])
        rename_mapping = {
            'Open': 'open_price',
            'High': 'high_price',
            'Low': 'low_price',
            'Close': 'close_price',
            'Volume': 'volume'
        }
        data_records = data_records.rename(columns=rename_mapping)
        required_columns = ['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']
        for col in required_columns:
            if col not in data_records.columns:
                return []
        data_records = data_records[required_columns].dropna(subset=required_columns)
        processed_records = []
        for _, row in data_records.iterrows():
            record_timestamp = row['timestamp']
            if daily:
                record_timestamp = record_timestamp.replace(hour=8, minute=0, second=0, microsecond=0)
            else:
                if record_timestamp.hour < 8:
                    record_timestamp = record_timestamp.replace(hour=8, minute=0, second=0, microsecond=0)
                elif record_timestamp.hour >= 24:
                    record_timestamp = record_timestamp.replace(hour=23, minute=0, second=0, microsecond=0)
                else:
                    record_timestamp = record_timestamp.replace(minute=0, second=0, microsecond=0)
            processed_records.append({
                'timestamp': record_timestamp,
                'open_price': float(row['open_price']),
                'high_price': float(row['high_price']),
                'low_price': float(row['low_price']),
                'close_price': float(row['close_price']),
                'volume': float(row['volume'])
            })
        return processed_records

    def load_daily_data_for_range(self, stock_symbol: str, start_date: str, end_date: str):
        stock = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            return
        raw_data = self.fetch_data(stock_symbol, '1d', start_date, end_date)
        if raw_data is None:
            return
        processed = self.process_data(raw_data, daily=True)
        if processed:
            self.repository.bulk_upsert_data(stock, processed)
            stock.data_availability = True
            stock.save()

    def load_hourly_data_for_range(self, stock_symbol: str, start_date: str, end_date: str):
        stock = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            return
        raw_data = self.fetch_data(stock_symbol, '1h', start_date, end_date)
        if raw_data is None:
            return
        processed = self.process_data(raw_data, daily=False)
        if processed:
            self.repository.bulk_upsert_data(stock, processed)
            stock.data_availability = True
            stock.save()

    def get_all_data(self) -> List[dict]:
        return self.repository.get_all_data()

    def get_latest_data_for_stock(self, stock_symbol: str) -> Optional[dict]:
        stock = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            return None
        latest_record = self.repository.get_latest_record(stock)
        if not latest_record:
            return None
        return {
            'stock_symbol': stock.stock_symbol,
            'timestamp': latest_record.timestamp.isoformat(),
            'open_price': str(latest_record.open_price),
            'high_price': str(latest_record.high_price),
            'low_price': str(latest_record.low_price),
            'close_price': str(latest_record.close_price),
            'volume': str(latest_record.volume)
        }

    def get_stock_data(self, stock_symbol: str, frequency: str, range_param: str) -> Optional[List[dict]]:
        stock = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            return None
        end_date = timezone.now()
        if range_param == "last_month":
            start_date = end_date - timedelta(days=31)
        elif range_param == "all_data":
            start_date = None
        else:
            start_date = end_date - timedelta(days=31)
        queryset = self.repository.get_data_raw(stock, start_date, end_date)
        if frequency == "daily":
            aggregated = queryset.annotate(date=TruncDate('timestamp')).values('date').annotate(
                open_price=Min('open_price'),
                high_price=Max('high_price'),
                low_price=Min('low_price'),
                close_price=Max('close_price'),
                volume=Sum('volume')
            ).order_by('date')
            result = []
            for record in aggregated:
                combined_date = datetime.combine(record['date'], datetime.min.time())
                result.append({
                    'timestamp': combined_date.isoformat(),
                    'open_price': str(record['open_price']),
                    'high_price': str(record['high_price']),
                    'low_price': str(record['low_price']),
                    'close_price': str(record['close_price']),
                    'volume': str(record['volume'])
                })
            return result
        elif frequency == "hourly":
            data_list = []
            for item in queryset:
                data_list.append({
                    'timestamp': item.timestamp.isoformat(),
                    'open_price': str(item.open_price),
                    'high_price': str(item.high_price),
                    'low_price': str(item.low_price),
                    'close_price': str(item.close_price),
                    'volume': str(item.volume)
                })
            return data_list
        return []



    def get_monthly_change(self, stock_symbol: str) -> Optional[dict]:
        stock = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            return None
        latest_record = self.repository.get_latest_record(stock)
        if not latest_record:
            return None

        monthly_ts = timezone.now() - timedelta(days=30)
        previous_record = self.repository.get_previous_record(stock, monthly_ts)
        if not previous_record:
            return None

        previous_close = float(previous_record.close_price)
        current_close = float(latest_record.close_price)
        if previous_close == 0.0:
            return None

        percent_change = ((current_close - previous_close) / previous_close) * 100
        return {
            "monthly_change": round(percent_change, 2)
        }

    def get_weekly_monthly_yearly_change(self, stock_symbol: str):
        stock = self.repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            return None
        latest_record = self.repository.get_latest_record(stock)
        if not latest_record:
            return None
        current_close = float(latest_record.close_price)

        weekly_ts = timezone.now() - timedelta(days=7)
        monthly_ts = timezone.now() - timedelta(days=30)
        yearly_ts = timezone.now() - timedelta(days=365)

        def get_change(ts):
            previous_record = self.repository.get_previous_record(stock, ts)
            if previous_record:
                old_close = float(previous_record.close_price)
                if old_close == 0:
                    return None
                return round(((current_close - old_close) / old_close) * 100, 2)
            return None

        weekly_change = get_change(weekly_ts)
        monthly_change = get_change(monthly_ts)
        yearly_change = get_change(yearly_ts)

        return {
            "weekly_change": f"{weekly_change}%" if weekly_change is not None else "N/A",
            "monthly_change": f"{monthly_change}%" if monthly_change is not None else "N/A",
            "yearly_change": f"{yearly_change}%" if yearly_change is not None else "N/A"
        }