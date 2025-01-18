from typing import List, Optional
from myapp.models import Stock, Exchange, Company

class StocksRepository:
    def get_all_stocks(self) -> List[Stock]:
        return list(Stock.objects.all())

    def get_stock_by_id(self, stock_id: int) -> Optional[Stock]:
        return Stock.objects.filter(pk=stock_id).first()

    def get_stock_by_symbol(self, symbol: str) -> Optional[Stock]:
        return Stock.objects.filter(stock_symbol__iexact=symbol).first()

    def add_stock(self, stock_symbol: str, stock_name: str, company: Company, exchange: Optional[Exchange] = None, share_class: str = None) -> Stock:
        if stock_name and len(stock_name) > 100:
            stock_name = stock_name[:100]
        stock = Stock(
            stock_symbol=stock_symbol,
            stock_name=stock_name,
            company=company,
            exchange=exchange,
            share_class=share_class
        )
        stock.save()
        return stock

    def update_stock(self, stock_id: int, stock_name: str = None, share_class: str = None) -> Optional[Stock]:
        stock = Stock.objects.filter(pk=stock_id).first()
        if stock:
            if stock_name is not None:
                stock.stock_name = stock_name
            if share_class is not None:
                stock.share_class = share_class
            stock.save()
            return stock
        return None

    def delete_stock(self, stock_id: int) -> bool:
        stock = Stock.objects.filter(pk=stock_id).first()
        if stock:
            stock.delete()
            return True
        return False
