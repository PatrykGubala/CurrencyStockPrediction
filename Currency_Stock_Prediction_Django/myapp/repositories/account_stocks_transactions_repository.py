from decimal import Decimal
from typing import List, Optional


from myapp.models import AccountStockTransaction
from myapp.utils.util_functions import normalize_decimal


class AccountStockTransactionRepository:
    def get_account_stock_transactions_by_account(self, account_id: int) -> List[AccountStockTransaction]:
        return list(AccountStockTransaction.objects.filter(account_id=account_id)
                    .select_related('stock', 'currency').order_by('-transaction_date'))

    def get_account_stock_transaction_by_id(self, transaction_id: int) -> Optional[AccountStockTransaction]:
        return AccountStockTransaction.objects.filter(id=transaction_id).first()

    def get_latest_account_stock_transaction(self, account_id: int, stock_id: int) -> Optional[AccountStockTransaction]:
        return AccountStockTransaction.objects.filter(
            account_id=account_id, stock_id=stock_id
        ).order_by('-transaction_date').first()

    def create_account_stock_transaction(self, account_id: int, transaction_type: str, stock_id: int,
                                         shares: float, price_per_share: float, currency_id: int,
                                         transaction_fee: float = 0.0, title: Optional[str] = None) -> AccountStockTransaction:

        shares = normalize_decimal(shares)
        price_per_share = normalize_decimal(price_per_share)
        transaction_fee = normalize_decimal(transaction_fee)

        if shares <= Decimal('0'):
            raise ValueError("Transaction shares must be positive")
        if price_per_share <= Decimal('0'):
            raise ValueError("Price per share must be positive")
        if transaction_fee < Decimal('0'):
            raise ValueError("Transaction fee cannot be negative")

        title = title or ('Kupno akcji' if transaction_type == 'buy' else 'Stock Sale')
        transaction = AccountStockTransaction(
            account_id=account_id, transaction_type=transaction_type,
            title=title, stock_id=stock_id, shares=shares,
            price_per_share=price_per_share, currency_id=currency_id,
            transaction_fee=transaction_fee
        )
        transaction.full_clean()
        transaction.save()
        return transaction

