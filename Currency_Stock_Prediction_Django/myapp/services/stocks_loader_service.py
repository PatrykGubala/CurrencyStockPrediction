import time
from collections import defaultdict

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from decouple import config

from myapp.apps import logger
from myapp.repositories.countries_repository import CountriesRepository
from myapp.repositories.exchanges_repository import ExchangeRepository
from myapp.repositories.companies_repository import CompanyRepository
from myapp.repositories.stocks_repository import StocksRepository
from datetime import datetime



class PolygonStocksLoaderService:
    def __init__(self):
        self.key = config('POLYGON_API_KEY', default='')
        self.exchanges_repo = ExchangeRepository()
        self.companies_repo = CompanyRepository()
        self.countries_repo = CountriesRepository()
        self.stocks_repo = StocksRepository()

    def fetch_stock_by_ticker(self, ticker: str):
        logger.info(f"Fetching stock details for ticker: {ticker}")
        url = f'https://api.polygon.io/v3/reference/tickers/{ticker}'
        params = {
            'apiKey': self.key,
            'active': 'true'
        }
        logger.debug(f"API request URL: {url} with params: {params}")
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            time.sleep(0.5)
            data = response.json()
            result = data.get('results')
            if result:
                logger.debug(f"Received data for {ticker}: {result}")
            else:
                logger.warning(f"No results found for ticker: {ticker}")
            return result
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 429:
                logger.error(f"Rate limit reached for {ticker}. Sleeping for 60 seconds.")
                time.sleep(60)
            logger.error(f"Error fetching details for {ticker}: {e}")
            return None

    def load_stocks_for_selected_countries(self):
        logger.info("Starting to load stocks for selected countries")
        countries_exchanges = {
            'US': {
                'name': 'United States',
                'exchanges': ['XNAS', 'NYSE']
            }
        }
        tickers_by_exchange = {
            'XNAS': [
                'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META',

            ],
            'NYSE': [
                'JNJ', 'V', 'WMT', 'DIS', 'BAC',

            ]
        }
        total_loaded = 0
        for country_code, info in countries_exchanges.items():
            country_name = info['name']
            exchanges_list = info['exchanges']
            logger.info(f"Processing country: {country_name} ({country_code})")
            country = self.countries_repo.get_country_by_code(country_code)
            if not country:
                logger.info(f"Creating new country record for {country_name}")
                country = self.countries_repo.add_country(
                    country_code=country_code,
                    country_name=country_name
                )
            for exchange_code in exchanges_list:
                logger.info(f"Processing exchange: {exchange_code} in {country_name}")
                tickers = tickers_by_exchange.get(exchange_code, [])
                logger.info(f"Found {len(tickers)} tickers for exchange {exchange_code}")
                for ticker in tickers:
                    existing_stock = self.stocks_repo.get_stock_by_symbol(ticker)
                    if existing_stock:
                        logger.debug(f"Stock {ticker} already exists, skipping API call")
                        continue
                    retry_count = 0
                    max_retries = 5
                    stock_info = self.fetch_stock_by_ticker(ticker)
                    while not stock_info and retry_count < max_retries:
                        logger.info(f"Data not available for {ticker}, waiting for 10 seconds.")
                        time.sleep(10)
                        retry_count += 1
                        stock_info = self.fetch_stock_by_ticker(ticker)
                    if not stock_info:
                        logger.warning(f"Data could not be retrieved for {ticker} after {max_retries} attempts. Skipping.")
                        continue
                    logger.debug(f"Processing stock: {ticker} - {stock_info.get('name')}")
                    mic = stock_info.get('primary_exchange', '')
                    if not mic:
                        logger.warning(f"No primary exchange found for ticker {ticker}")
                        continue
                    exchange = self.exchanges_repo.get_exchange_by_name(mic)
                    if not exchange:
                        logger.info(f"Creating new exchange: {mic} for country {country_name}")
                        exchange = self.exchanges_repo.add_exchange(mic, country=country)
                    elif exchange.country is None:
                        logger.info(f"Updating exchange {mic} with country {country_name}")
                        exchange.country = country
                        exchange.save()
                    desc = stock_info.get('name', '')
                    if not ticker:
                        logger.warning("Stock missing ticker symbol, skipping")
                        continue
                    company = self.companies_repo.get_company_by_symbol(ticker)
                    if not company:
                        logger.info(f"Creating new company: {ticker} - {desc}")
                        company = self.companies_repo.add_company(
                            ticker,
                            desc,
                            country
                        )
                    stock = self.stocks_repo.get_stock_by_symbol(ticker)
                    if not stock:
                        logger.info(f"Creating new stock: {ticker} on exchange {mic}")
                        self.stocks_repo.add_stock(ticker, desc, company, exchange, None)
                        total_loaded += 1
                    else:
                        logger.debug(f"Stock {ticker} already exists, skipping")
        logger.info(f"Finished loading stocks. Total new stocks loaded: {total_loaded}")
        return total_loaded




    @api_view(['POST'])
    def load_stocks_exchanges_companies(request):
        logger.info("Starting stock loading process")
        loader = PolygonStocksLoaderService()
        created_stocks = loader.load_stocks_for_selected_countries()
        logger.info(f"Process completed. Loaded {created_stocks} stocks ")
        return Response(
            {"loaded_stocks": created_stocks},
            status=status.HTTP_201_CREATED
        )


