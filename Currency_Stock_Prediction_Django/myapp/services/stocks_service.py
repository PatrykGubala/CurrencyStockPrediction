from typing import List, Optional
from myapp.repositories.companies_repository import CompanyRepository
from myapp.repositories.exchanges_repository import ExchangeRepository
from myapp.repositories.stocks_repository import StocksRepository

class StocksService:
    def __init__(self):
        self.stocks_repo = StocksRepository()
        self.exchange_repo = ExchangeRepository()
        self.company_repo = CompanyRepository()

    def get_all_stocks_dto(self) -> List[dict]:
        stocks = self.stocks_repo.get_all_stocks()
        return [
            {
                "id": stock.id,
                "symbol": stock.stock_symbol,
                "name": stock.stock_name,
                "company_id": stock.company.id,
                "exchange_id": stock.exchange.id if stock.exchange else None,
                "share_class": stock.share_class,
                "data_availability": stock.data_availability
            }
            for stock in stocks
        ]

    def add_stock(self, stock_symbol: str, stock_name: str, company_symbol: str, exchange_name: Optional[str] = None, share_class: Optional[str] = None) -> dict:
        company = self.company_repo.get_company_by_symbol(company_symbol)
        if not company:
            company = self.company_repo.add_company(company_symbol, stock_name)
        exchange = None
        if exchange_name:
            exchange = self.exchange_repo.get_exchange_by_name(exchange_name)
            if not exchange:
                exchange = self.exchange_repo.add_exchange(exchange_name)
        created_stock = self.stocks_repo.add_stock(stock_symbol, stock_name, company, exchange, share_class)
        return {
            "id": created_stock.id,
            "symbol": created_stock.stock_symbol,
            "name": created_stock.stock_name,
            "company_id": created_stock.company.id,
            "exchange_id": created_stock.exchange.id if created_stock.exchange else None,
            "share_class": created_stock.share_class
        }

    def update_stock(self, stock_id: int, stock_name: str = None, share_class: str = None) -> Optional[dict]:
        updated_stock = self.stocks_repo.update_stock(stock_id, stock_name, share_class)
        if not updated_stock:
            return None
        return {
            "id": updated_stock.id,
            "symbol": updated_stock.stock_symbol,
            "name": updated_stock.stock_name,
            "company_id": updated_stock.company.id,
            "exchange_id": updated_stock.exchange.id if updated_stock.exchange else None,
            "share_class": updated_stock.share_class
        }

    def delete_stock(self, stock_id: int) -> bool:
        return self.stocks_repo.delete_stock(stock_id)
