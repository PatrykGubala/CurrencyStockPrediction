from decimal import Decimal
from typing import Optional, List

from django.db import transaction

from myapp.models import AccountStock, Stock, AccountStockTransaction
from myapp.utils.util_functions import normalize_decimal


class AccountStocksRepository:
    def get_account_stock_holding_by_id(self, account_id: int, stock_id: int) -> Optional[AccountStock]:
        return AccountStock.objects.filter(account_id=account_id, stock_id=stock_id).select_related('stock').first()

    def get_account_stock_holding_by_symbol(self, account_id: int, stock_symbol: str) -> Optional[AccountStock]:
        return AccountStock.objects.filter(account_id=account_id, stock__stock_symbol__iexact=stock_symbol).select_related('stock').first()

    def get_all_account_stocks(self, account_id: int) -> List[AccountStock]:
        return list(AccountStock.objects.filter(account_id=account_id).select_related('stock'))

    def create_account_stock_holding(self, account_id: int, stock_id: int, shares: float = 0.0) -> AccountStock:
        shares = normalize_decimal(shares)
        if shares < Decimal('0'):
            raise ValueError("Initial shares cannot be negative")
        holding = AccountStock(account_id=account_id, stock_id=stock_id, shares=shares)
        holding.full_clean()
        holding.save()
        return holding

    def update_account_stocks_shares(self, account_id: int, stock_id: int, new_shares: float) -> Optional[AccountStock]:
        if new_shares < 0:
            raise ValueError("Shares quantity cannot be negative")
        holding = self.get_account_stock_holding_by_id(account_id, stock_id)
        if holding:
            holding.shares = new_shares
            holding.full_clean()
            holding.save()
        return holding

    def delete_account_stock_holding(self, account_id: int, stock_id: int) -> bool:
        holding = self.get_account_stock_holding_by_id(account_id, stock_id)
        if holding:
            holding.delete()
            return True
        return False

