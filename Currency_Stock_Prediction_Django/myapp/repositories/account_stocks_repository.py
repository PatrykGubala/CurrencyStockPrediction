from typing import Optional, List
from myapp.models import AccountStock, Stock, AccountStockTransaction

class AccountStocksRepository:
    def get_by_account_and_stock(self, account_id: int, stock_id: int) -> Optional[AccountStock]:
        return AccountStock.objects.filter(account_id=account_id, stock_id=stock_id).first()

    def get_by_account_and_symbol(self, account_id: int, stock_symbol: str) -> Optional[AccountStock]:
        return AccountStock.objects.filter(
            account_id=account_id,
            stock__stock_symbol__iexact=stock_symbol
        ).select_related('stock').first()

    def add_account_stock(self, account_id: int, stock_id: int, shares: float) -> AccountStock:
        account_stock = AccountStock(account_id=account_id, stock_id=stock_id, shares=shares)
        account_stock.save()
        return account_stock

    def get_account_stocks(self, account_id: int) -> List[AccountStock]:
        return list(AccountStock.objects.filter(account_id=account_id).select_related('stock'))

    def update_shares(self, account_id: int, stock_id: int, shares: float) -> Optional[AccountStock]:
        account_stock = self.get_by_account_and_stock(account_id, stock_id)
        if account_stock:
            account_stock.shares = shares
            account_stock.save()
        return account_stock

    def delete_account_stock(self, account_id: int, stock_id: int) -> bool:
        account_stock = self.get_by_account_and_stock(account_id, stock_id)
        if account_stock:
            account_stock.delete()
            return True
        return False

    def create_transaction(self, account_id: int, transaction_type: str, stock_id: int,
                         shares: float, price_per_share: float, currency_id: int,
                         transaction_fee: float) -> AccountStockTransaction:
        return AccountStockTransaction.objects.create(
            account_id=account_id,
            transaction_type=transaction_type,
            title='Stock Purchase' if transaction_type == 'buy' else 'Stock Sale',
            stock_id=stock_id,
            shares=shares,
            price_per_share=price_per_share,
            currency_id=currency_id,
            transaction_fee=transaction_fee
        )

    def get_transactions(self, account_id: int) -> List[AccountStockTransaction]:
        return list(AccountStockTransaction.objects.filter(account_id=account_id)
                   .select_related('stock', 'currency').order_by('-transaction_date'))