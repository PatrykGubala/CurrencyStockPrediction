from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import yfinance as yf
from django.db.models import Min, Max, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from myapp.models import Currency, CurrenciesData
from myapp.repositories.currencies_data_repository import CurrenciesDataRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrenciesDataService:
    def __init__(self):
        self.repository = CurrenciesDataRepository()

    def load_daily_data_for_range(self, currency_code, start_date, end_date):
        currency = self.repository.get_currency_by_code(currency_code)
        if not currency:
            return
        daily_data = self.fetch_data(currency, frequency='1d', start_date=start_date, end_date=end_date)
        if daily_data is not None:
            processed = self.process_data(daily_data, daily=True)
            if processed:
                self.repository.bulk_upsert_data(currency, processed)
                currency.data_availability = True
                currency.save()

    def load_hourly_data_for_range(self, currency_code, start_date, end_date):
        currency = self.repository.get_currency_by_code(currency_code)
        if not currency:
            return
        hourly_data = self.fetch_data(currency, frequency='1h', start_date=start_date, end_date=end_date)
        if hourly_data is not None:
            processed = self.process_data(hourly_data, daily=False)
            if processed:
                self.repository.bulk_upsert_data(currency, processed)
                currency.data_availability = True
                currency.save()



    def fetch_data(self, currency: Currency, frequency: str, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        try:
            ticker_name = "USD" + currency.code + "=X"

            ticker = yf.Ticker(ticker_name)
            hist = ticker.history(start=start_date, end=end_date, interval=frequency)
            if hist.empty:
                logger.warning(f"{currency.code}: No data returned from yfinance for interval: {frequency} between {start_date} and {end_date}")
                return None
            hist = hist.reset_index()
            if 'Datetime' in hist.columns:
                hist['Datetime'] = pd.to_datetime(hist['Datetime'], utc=True)
                hist = hist[(hist['Datetime'].dt.hour >= 8) & (hist['Datetime'].dt.hour < 24)]
                hist['Datetime'] = hist['Datetime'].dt.floor('h')
            elif 'Date' in hist.columns:
                hist['Date'] = pd.to_datetime(hist['Date'], utc=True)
                hist['Date'] = hist['Date'].dt.floor('D')
            logger.info(f"Data fetched for currency: {currency.code} with {len(hist)} rows and interval: {frequency}")
            return hist
        except Exception as e:
            logger.error(f"Error fetching data for currency {currency.code} with interval {frequency}: {e}")
            return None

    def process_data(self, data_records: pd.DataFrame, daily: bool) -> List[dict]:
        if 'Date' in data_records.columns:
            data_records = data_records.rename(columns={'Date': 'timestamp'})
        elif 'Datetime' in data_records.columns:
            data_records = data_records.rename(columns={'Datetime': 'timestamp'})
        data_records = data_records.dropna(subset=['timestamp'])
        data_records['timestamp'] = pd.to_datetime(data_records['timestamp'], utc=True)
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
        processed = []
        for _, row in data_records.iterrows():
            timestamp = row['timestamp']
            if daily:
                timestamp = timestamp.replace(hour=8, minute=0, second=0, microsecond=0)
            else:
                if timestamp.hour < 8:
                    timestamp = timestamp.replace(hour=8, minute=0, second=0, microsecond=0)
                elif timestamp.hour >= 24:
                    timestamp = timestamp.replace(hour=23, minute=0, second=0, microsecond=0)
                else:
                    timestamp = timestamp.replace(minute=0, second=0, microsecond=0)
            record = {
                'timestamp': timestamp,
                'open_price': float(row['open_price']),
                'high_price': float(row['high_price']),
                'low_price': float(row['low_price']),
                'close_price': float(row['close_price']),
                'volume': float(row['volume'])
            }
            processed.append(record)
        return processed

    def get_all_data(self) -> List[dict]:
        return self.repository.get_all_data()

    def get_latest_data_for_currency(self, currency_id: int) -> Optional[dict]:
        currency = self.repository.get_currency_by_id(currency_id)
        if not currency:
            return None
        latest = self.repository.get_latest_record(currency)
        if not latest:
            return None
        return {
            'currency_id': currency.id,
            'timestamp': latest.timestamp,
            'open': str(latest.open_price),
            'high': str(latest.high_price),
            'low': str(latest.low_price),
            'close': str(latest.close_price),
            'volume': str(latest.volume)
        }

    def get_percentage_change(self, currency_id: int) -> Optional[dict]:
        currency = self.repository.get_currency_by_id(currency_id)
        if not currency:
            return None
        latest = self.repository.get_latest_record(currency)
        if not latest:
            return None
        previous = self.repository.get_previous_record(currency, latest.timestamp)
        if not previous:
            return None
        previous_close = float(previous.close_price)
        current_close = float(latest.close_price)
        if previous_close == 0.0:
            return None
        percent_change = ((current_close - previous_close) / previous_close) * 100
        return {
            'currency_id': currency.id,
            'latest_timestamp': latest.timestamp,
            'current_close': str(current_close),
            'previous_close': str(previous_close),
            'percent_change': str(percent_change)
        }

    def get_currency_data(self, currency_code: str, frequency: str, range_param: str) -> Optional[List[dict]]:
        currency = self.repository.get_currency_by_code(currency_code)
        if not currency:
            return None
        end_date = timezone.now()
        if range_param == "last_month":
            start_date = end_date - timedelta(days=31)
        elif range_param == "all_data":
            start_date = None
        else:
            start_date = end_date - timedelta(days=31)
        data_queryset = self.repository.get_data_raw(currency, frequency, start_date, end_date)
        if frequency == "daily":
            aggregated_data = data_queryset.annotate(
                date=TruncDate('timestamp')
            ).values('date').annotate(
                open_price=Min('open_price'),
                high_price=Max('high_price'),
                low_price=Min('low_price'),
                close_price=Max('close_price'),
                volume=Sum('volume')
            ).order_by('date')
            formatted_data = []
            for record in aggregated_data:
                formatted_data.append({
                    'timestamp': datetime.combine(record['date'], datetime.min.time()).timestamp() * 1000,
                    'open': str(record['open_price']),
                    'high': str(record['high_price']),
                    'low': str(record['low_price']),
                    'close': str(record['close_price']),
                    'volume': str(record['volume']),
                })
            return formatted_data
        elif frequency == "hourly":
            data = []
            for entry in data_queryset:
                data.append({
                    'timestamp': entry.timestamp.timestamp() * 1000,
                    'open': str(entry.open_price),
                    'high': str(entry.high_price),
                    'low': str(entry.low_price),
                    'close': str(entry.close_price),
                    'volume': str(entry.volume),
                })
            return data
        return None


    def get_monthly_change(self, currency_code: str) -> Optional[dict]:
        currency = self.repository.get_currency_by_code(currency_code)
        if not currency:
            return None

        latest = self.repository.get_latest_record(currency)
        if not latest:
            return None

        monthly_ts = timezone.now() - timedelta(days=30)
        record = self.repository.get_previous_record(currency, monthly_ts)
        if not record:
            return None

        previous_close = float(record.close_price)
        current_close = float(latest.close_price)
        if previous_close == 0.0:
            return None

        percent_change = ((current_close - previous_close) / previous_close) * 100
        return {
            "monthly_change": round(percent_change, 2)
        }


    def get_weekly_monthly_yearly_change(self, currency_code: str):
        currency = self.repository.get_currency_by_code(currency_code)
        if not currency:
            return None

        latest = self.repository.get_latest_record(currency)
        if not latest:
            return None
        current_close = float(latest.close_price)

        weekly_ts = timezone.now() - timedelta(days=7)
        monthly_ts = timezone.now() - timedelta(days=30)
        yearly_ts = timezone.now() - timedelta(days=365)

        def get_change(ts):
            record = self.repository.get_previous_record(currency, ts)
            if record:
                old_close = float(record.close_price)
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