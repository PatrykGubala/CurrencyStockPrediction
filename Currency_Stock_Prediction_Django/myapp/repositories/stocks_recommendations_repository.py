from typing import List
from myapp.models import Stock, StocksRecommendation

class StockRecommendationsRepository:
    def create_recommendation(self, stock: Stock, date, buy: int, hold: int, sell: int, strong_buy: int, strong_sell: int) -> StocksRecommendation:
        recommendation = StocksRecommendation(
            stock=stock,
            date=date,
            buy=buy,
            hold=hold,
            sell=sell,
            strong_buy=strong_buy,
            strong_sell=strong_sell
        )
        recommendation.save()
        return recommendation

    def get_recommendations_for_stock(self, stock: Stock) -> List[StocksRecommendation]:
        return list(StocksRecommendation.objects.filter(stock=stock).order_by('-date'))

    def get_all_recommendations(self) -> List[StocksRecommendation]:
        return list(StocksRecommendation.objects.all().order_by('-date'))
