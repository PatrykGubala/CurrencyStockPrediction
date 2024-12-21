from datetime import datetime, timedelta
from typing import Optional, List
import pandas as pd
import yfinance as yf
from django.utils import timezone
from myapp.models import Currency
from myapp.repositories.currencies_data_repository import CurrenciesDataRepository
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurrenciesDataService:
    def __init__(self):
        self.repository = CurrenciesDataRepository()

    def load_hourly_data(self, currency_ids=None):
        logger.info("Starting hourly data load process")
        currencies = Currency.objects.all()
        if currency_ids:
            currencies = currencies.filter(id__in=currency_ids)
        for currency in currencies:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=31)
            hourly_data = self.fetch_data(
                currency,
                frequency='1h',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            if hourly_data is not None:
                processed_hourly = self.process_data(hourly_data, daily=False)
                if processed_hourly:
                    self.repository.bulk_upsert_data(currency, processed_hourly)
                    currency.data_availability = True
                    currency.save()
                    logger.info(f"Successfully loaded hourly data for currency: {currency.code}")
        logger.info("Hourly data load process completed")

    def load_daily_data(self, currency_ids=None):
        logger.info("Starting daily data load process")
        currencies = Currency.objects.all()
        if currency_ids:
            currencies = currencies.filter(id__in=currency_ids)
        for currency in currencies:
            start_date = datetime(2013, 1, 1)
            start_date = timezone.make_aware(start_date, timezone.get_current_timezone())
            end_date = timezone.now().strftime('%Y-%m-%d')
            daily_data = self.fetch_data(
                currency,
                frequency='1d',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date
            )
            if daily_data is not None:
                processed_daily = self.process_data(daily_data, daily=True)
                if processed_daily:
                    self.repository.bulk_upsert_data(currency, processed_daily)
                    currency.data_availability = True
                    currency.save()
                    logger.info(f"Successfully loaded daily data for currency: {currency.code}")
        logger.info("Daily data load process completed")

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
