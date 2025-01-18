from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import finnhub
from decouple import config
from myapp.repositories.exchanges_repository import ExchangeRepository
from myapp.repositories.companies_repository import CompanyRepository
from myapp.repositories.stocks_repository import StocksRepository
from myapp.repositories.stocks_recommendations_repository import StockRecommendationsRepository
from datetime import datetime

class FinnhubStocksLoaderService:
    def __init__(self):
        self.key = config('FINNHUB_API_KEY', default='')
        self.client = finnhub.Client(api_key=self.key)
        self.exchanges_repo = ExchangeRepository()
        self.companies_repo = CompanyRepository()
        self.stocks_repo = StocksRepository()
        self.recs_repo = StockRecommendationsRepository()

    def load_all_us_stocks(self):
        data = self.client.stock_symbols('US')
        count = 0
        for i in data:
            e = self.exchanges_repo.get_exchange_by_name(i.get('mic'))
            if not e:
                e = self.exchanges_repo.add_exchange(i.get('mic'))
            c = self.companies_repo.get_company_by_symbol(i.get('symbol'))
            if not c:
                c = self.companies_repo.add_company(i.get('symbol'), i.get('description'), None)
            s = self.stocks_repo.get_stock_by_symbol(i.get('symbol'))
            if not s:
                self.stocks_repo.add_stock(i.get('symbol'), i.get('description'), c, e, None)
                count += 1
        return count

    def load_recommendations_for_all_us_stocks(self):
        data = self.client.stock_symbols('US')
        count = 0
        for i in data:
            s = self.stocks_repo.get_stock_by_symbol(i.get('symbol'))
            if s:
                r = self.client.recommendation_trends(i.get('symbol'))
                for item in r:
                    p = item.get('period')
                    if p:
                        dt = datetime.strptime(p, "%Y-%m-%d").date()
                        buy = item.get('buy', 0)
                        hold = item.get('hold', 0)
                        sell = item.get('sell', 0)
                        sb = item.get('strongBuy', 0)
                        ss = item.get('strongSell', 0)
                        self.recs_repo.create_recommendation(s, dt, buy, hold, sell, sb, ss)
                        count += 1
        return count

@api_view(['POST'])
def load_all_us_stocks_with_recommendations(request):
    loader = FinnhubStocksLoaderService()
    created_stocks = loader.load_all_us_stocks()
    created_recs = loader.load_recommendations_for_all_us_stocks()
    return Response({"loaded_stocks": created_stocks, "created_recommendations": created_recs}, status=status.HTTP_201_CREATED)
