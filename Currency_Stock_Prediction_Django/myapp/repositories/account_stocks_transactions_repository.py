from typing import List, Optional
from django.db.models import Q
from myapp.models import AccountStockTransaction

class AccountStockTransactionRepository:
    def create_transaction(self, transaction_data: dict) -> AccountStockTransaction:
        transaction = AccountStockTransaction(**transaction_data)
        transaction.save()
        return transaction

    def get_transactions_by_account(self, account_id: int) -> List[AccountStockTransaction]:
        return list(AccountStockTransaction.objects.filter(
            account_id=account_id
        ).select_related('stock', 'currency').order_by('-transaction_date'))

    def get_transaction_by_id(self, transaction_id: int) -> Optional[AccountStockTransaction]:
        return AccountStockTransaction.objects.filter(id=transaction_id).first()

    def get_latest_transaction(self, account_id: int, stock_id: int) -> Optional[AccountStockTransaction]:
        return AccountStockTransaction.objects.filter(
            account_id=account_id,
            stock_id=stock_id
        ).order_by('-transaction_date').first()