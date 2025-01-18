import os
import time

import finnhub
import requests
from finnhub import FinnhubAPIException
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


class FinnhubSafeClient:
    def __init__(self):
        self.client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)
        self.retry_count = 3
        self.retry_delay = 2  # seconds

    def _handle_request(self, operation_name, func, *args, **kwargs):
        for attempt in range(self.retry_count):
            try:
                result = func(*args, **kwargs)
                return result
            except (FinnhubAPIException, requests.exceptions.ReadTimeout) as e:
                logger.error(f"Attempt {attempt + 1}/{self.retry_count} failed for {operation_name}: {str(e)}")
                if attempt == self.retry_count - 1:
                    raise RuntimeError(f"FinnhubAPIException in {operation_name} after {self.retry_count} attempts: {str(e)}")
                time.sleep(self.retry_delay)
            except Exception as e:
                logger.error(f"Unexpected error in {operation_name}: {str(e)}")
                raise RuntimeError(f"Unexpected error in {operation_name}: {str(e)}")

    def stock_symbols(self, exchange):
        return self._handle_request(
            'stock_symbols',
            self.client.stock_symbols,
            exchange
        )

    def recommendation_trends(self, symbol):
        return self._handle_request(
            'recommendation_trends',
            self.client.recommendation_trends,
            symbol
        )

    def company_profile2(self, symbol=None, isin=None, cusip=None):
        return self._handle_request(
            'company_profile2',
            self.client.company_profile2,
            symbol=symbol,
            isin=isin,
            cusip=cusip
        )

    def stock_candles(self, symbol, resolution, start, end):
        return self._handle_request(
            'stock_candles',
            self.client.stock_candles,
            symbol,
            resolution,
            start,
            end
        )