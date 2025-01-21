from decimal import Decimal, ROUND_DOWN
from typing import Optional, List, Union
from django.db import transaction
from django.utils import timezone

from myapp.repositories.account_stocks_repository import AccountStocksRepository
from myapp.repositories.account_stocks_transactions_repository import AccountStockTransactionRepository
from myapp.repositories.stocks_data_repository import StocksDataRepository
from myapp.repositories.stocks_repository import StocksRepository
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository

class AccountStocksService:
    FEE_RATE = Decimal('0.005')

    def __init__(self):
        self.account_stocks_repository = AccountStocksRepository()
        self.stocks_repository = StocksRepository()
        self.stocks_data_repository = StocksDataRepository()
        self.account_currencies_repository = AccountCurrenciesRepository()
        self.account_stock_transaction_repository = AccountStockTransactionRepository()

    def normalize_decimal(self, value: Union[str, float, Decimal]) -> Decimal:
        if isinstance(value, float):
            value = str(value)
        return Decimal(value).quantize(Decimal('0.00000000'), rounding=ROUND_DOWN)

    def get_account_stock_balance(self, account_id: int, stock_symbol: str) -> dict:
        account_stock = self.account_stocks_repository.get_account_stock_holding_by_symbol(account_id, stock_symbol)
        shares = account_stock.shares if account_stock else Decimal(0)
        return {
            "stock_symbol": stock_symbol,
            "shares": str(shares)
        }

    def buy_stock(self, account_id: int, stock_symbol: str, shares: float) -> bool:
        if shares <= 0:
            raise ValueError("Shares amount must be positive")
        stock = self.stocks_repository.get_stock_by_symbol(stock_symbol)
        if not stock:
            raise ValueError(f"Stock {stock_symbol} not found")
        latest_data = self.stocks_data_repository.get_latest_stock_data(stock_symbol)
        if not latest_data:
            raise ValueError("No stock data available for price determination")
        price_per_share = Decimal(str(latest_data.close_price))
        cost_without_fee = price_per_share * Decimal(str(shares))
        fee = cost_without_fee * Decimal("0.005")
        total_cost = cost_without_fee + fee
        usd_account = self.account_currencies_repository.get_account_currency_balance_by_id(account_id, 1)
        if not usd_account or usd_account.balance < total_cost:
            raise ValueError("Insufficient USD balance")
        with transaction.atomic():
            new_usd_balance = usd_account.balance - total_cost
            self.account_currencies_repository.update_account_currency_balance(account_id, 1, float(new_usd_balance))
            account_stock = self.account_stocks_repository.get_account_stock_holding_by_symbol(account_id, stock_symbol)
            if not account_stock:
                self.account_stocks_repository.create_account_stock_holding(account_id, stock.id, float(shares))
            else:
                new_shares = float(account_stock.shares + Decimal(str(shares)))
                self.account_stocks_repository.update_account_stocks_shares(account_id, stock.id, new_shares)
            self.account_stock_transaction_repository.create_account_stock_transaction(
                account_id=account_id,
                transaction_type='buy',
                stock_id=stock.id,
                shares=float(shares),
                price_per_share=float(price_per_share),
                currency_id=1,
                transaction_fee=float(fee)
            )
        return True

    def sell_stock(self, account_id: int, stock_symbol: str, shares: float) -> bool:
        if shares <= 0:
            raise ValueError("Shares amount must be positive")
        account_stock = self.account_stocks_repository.get_account_stock_holding_by_symbol(account_id, stock_symbol)
        if not account_stock or account_stock.shares < Decimal(str(shares)):
            raise ValueError(f"Insufficient {stock_symbol} shares")
        latest_data = self.stocks_data_repository.get_latest_stock_data(stock_symbol)
        if not latest_data:
            raise ValueError("No stock data available for price determination")
        price_per_share = Decimal(str(latest_data.close_price))
        revenue_without_fee = price_per_share * Decimal(str(shares))
        fee = revenue_without_fee * Decimal("0.005")
        total_revenue = revenue_without_fee - fee
        with transaction.atomic():
            new_shares = float(account_stock.shares - Decimal(str(shares)))
            self.account_stocks_repository.update_account_stocks_shares(account_id, account_stock.stock.id, new_shares)
            usd_account = self.account_currencies_repository.get_account_currency_balance_by_id(account_id, 1)
            if not usd_account:
                raise ValueError("USD account not found")
            new_usd_balance = float(usd_account.balance + total_revenue)
            self.account_currencies_repository.update_account_currency_balance(account_id, 1, new_usd_balance)
            self.account_stock_transaction_repository.create_account_stock_transaction(
                account_id=account_id,
                transaction_type='sell',
                stock_id=account_stock.stock.id,
                shares=float(shares),
                price_per_share=float(price_per_share),
                currency_id=1,
                transaction_fee=float(fee)
            )
        return True

    def get_transactions(self, account_id: int) -> List[dict]:
        transactions = self.account_stock_transaction_repository.get_account_stock_transactions_by_account(account_id)
        return [
            {
                'transaction_type': transaction.transaction_type,
                'stock_symbol': transaction.stock.stock_symbol,
                'shares': str(transaction.shares),
                'price_per_share': str(transaction.price_per_share),
                'transaction_fee': str(transaction.transaction_fee),
                'transaction_date': transaction.transaction_date.isoformat(),
                'total_cost': str(transaction.shares * transaction.price_per_share + transaction.transaction_fee)
            }
            for transaction in transactions
        ]
