import logging
from datetime import datetime
from decouple import config
import finnhub

from myapp.repositories.companies_repository import CompanyRepository
from myapp.repositories.exchanges_repository import ExchangeRepository
from myapp.repositories.stocks_recommendations_repository import StockRecommendationsRepository
from myapp.repositories.stocks_repository import StocksRepository
from myapp.utils.finnhub_safe_client import FinnhubSafeClient

logger = logging.getLogger(__name__)


class FinnhubLoaderService:
    def __init__(self):
        self.client = FinnhubSafeClient()
        self.exchanges_repo = ExchangeRepository()
        self.companies_repo = CompanyRepository()
        self.stocks_repo = StocksRepository()
        self.recs_repo = StockRecommendationsRepository()

    def load_all_us_stocks(self):
        try:
            data = self.client.stock_symbols('US')
            logger.info("Fetched %s symbols from Finnhub for US market.", len(data))
            created_count = 0
            exchange_counts = {}

            for item in data:
                try:
                    mic = item.get('mic')
                    symbol = item.get('symbol')
                    description = item.get('description', '')

                    if not all([mic, symbol, description]):
                        logger.warning(f"Skipping incomplete data: {item}")
                        continue

                    if mic:
                        current_count = exchange_counts.get(mic, 0)
                        if current_count >= 10:
                            continue
                        exchange_counts[mic] = current_count + 1

                    exchange = None
                    if mic:
                        exchange = self.exchanges_repo.get_exchange_by_name(mic)
                        if not exchange:
                            exchange = self.exchanges_repo.add_exchange(mic)

                    company = self.companies_repo.get_company_by_symbol(symbol)
                    if not company:
                        # Try to get company profile for logo
                        try:
                            profile = self.client.company_profile2(symbol=symbol)
                            logo_url = profile.get('logo', None) if profile else None
                        except Exception as e:
                            logger.warning(f"Failed to fetch company profile for {symbol}: {e}")
                            logo_url = None

                        company = self.companies_repo.add_company(
                            company_symbol=symbol,
                            company_name=description,
                            logo_url=logo_url
                        )

                    stock = self.stocks_repo.get_stock_by_symbol(symbol)
                    if not stock:
                        self.stocks_repo.add_stock(
                            stock_symbol=symbol,
                            stock_name=description,
                            company=company,
                            exchange=exchange,
                            share_class=None
                        )
                        created_count += 1

                except Exception as e:
                    logger.error(f"Error processing stock item: {e}")
                    continue

            logger.info("Created %s new stocks in the database.", created_count)
            return created_count
        except Exception as e:
            logger.error(f"Failed to load US stocks: {e}")
            raise

    def load_recommendations_for_all_us_stocks(self):
        try:
            stocks = self.stocks_repo.get_all_stocks()
            logger.info("Processing recommendations for %s stocks.", len(stocks))
            created_count = 0

            for stock in stocks:
                try:
                    symbol = stock.stock_symbol
                    recommendations = self.client.recommendation_trends(symbol)
                    if not recommendations:
                        continue

                    for rec_item in recommendations:
                        try:
                            period_str = rec_item.get('period')
                            if not period_str:
                                continue

                            date_obj = datetime.strptime(period_str, "%Y-%m-%d").date()
                            buy = rec_item.get('buy', 0)
                            hold = rec_item.get('hold', 0)
                            sell = rec_item.get('sell', 0)
                            strong_buy = rec_item.get('strongBuy', 0)
                            strong_sell = rec_item.get('strongSell', 0)

                            self.recs_repo.create_recommendation(
                                stock=stock,
                                date=date_obj,
                                buy=buy,
                                hold=hold,
                                sell=sell,
                                strong_buy=strong_buy,
                                strong_sell=strong_sell
                            )
                            created_count += 1

                        except Exception as e:
                            logger.error(f"Error processing recommendation item for {symbol}: {e}")
                            continue

                except Exception as e:
                    logger.error(f"Error fetching recommendations for stock {stock.stock_symbol}: {e}")
                    continue

            logger.info("Created %s new recommendations in the database.", created_count)
            return created_count
        except Exception as e:
            logger.error(f"Failed to load recommendations: {e}")
            raise