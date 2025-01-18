import os
import finnhub
from datetime import datetime
from typing import List
from myapp.repositories.stocks_recommendations_repository import StockRecommendationsRepository
from myapp.repositories.stocks_repository import StocksRepository
from myapp.utils.finnhub_safe_client import FinnhubSafeClient

class StockRecommendationsService:
    def __init__(self):
        self.repository = StockRecommendationsRepository()
        self.stocks_repository = StocksRepository()
        self.finnhub_safe_client = FinnhubSafeClient()

    def load_recommendations_for_symbol(self, symbol: str) -> List[dict]:
        stock = self.stocks_repository.get_stock_by_symbol(symbol)
        if not stock:
            return []
        try:
            recommendations_data = self.finnhub_safe_client.recommendation_trends(symbol)
        except RuntimeError as e:
            print(f"Error loading recommendations: {e}")
            return []
        created_recommendations = []
        for recommendation_item in recommendations_data:
            date_str = recommendation_item.get('period')
            if not date_str:
                continue
            date_value = datetime.strptime(date_str, "%Y-%m-%d").date()
            buy_value = recommendation_item.get('buy', 0)
            hold_value = recommendation_item.get('hold', 0)
            sell_value = recommendation_item.get('sell', 0)
            strong_buy_value = recommendation_item.get('strongBuy', 0)
            strong_sell_value = recommendation_item.get('strongSell', 0)
            created = self.repository.create_recommendation(
                stock,
                date_value,
                buy_value,
                hold_value,
                sell_value,
                strong_buy_value,
                strong_sell_value
            )
            created_recommendations.append({
                "id": created.id,
                "stock_symbol": symbol,
                "date": str(created.date),
                "buy": created.buy,
                "hold": created.hold,
                "sell": created.sell,
                "strong_buy": created.strong_buy,
                "strong_sell": created.strong_sell,
                "created_at": created.created_at.isoformat()
            })
        return created_recommendations


    def load_recommendations_for_all_stocks(self):
        stocks = self.stocks_repository.get_all_stocks()
        total_recommendations = 0

        for stock in stocks:
            try:
                recs =self.load_recommendations_for_symbol(stock.stock_symbol)
                total_recommendations += len(recs)
            except Exception as e:
                print(f"Error loading recommendations for {stock.stock_symbol}: {str(e)}")
                continue
        return total_recommendations

    def get_recommendations_for_symbol(self, symbol: str) -> List[dict]:
        stock = self.stocks_repository.get_stock_by_symbol(symbol)
        if not stock:
            return []
        recommendations = self.repository.get_recommendations_for_stock(stock)
        return [
            {
                "id": recommendation.id,
                "stock_symbol": stock.stock_symbol,
                "date": str(recommendation.date),
                "buy": recommendation.buy,
                "hold": recommendation.hold,
                "sell": recommendation.sell,
                "strong_buy": recommendation.strong_buy,
                "strong_sell": recommendation.strong_sell,
                "created_at": recommendation.created_at.isoformat()
            }
            for recommendation in recommendations
        ]
