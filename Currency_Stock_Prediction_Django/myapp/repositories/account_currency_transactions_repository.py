from typing import Optional, List
from myapp.models.models import AccountCurrencyTransaction, Account

class AccountCurrencyTransactionsRepository:
    def create_transaction(
        self,
        sender_account: Optional[Account],
        receiver_account: Optional[Account],
        transaction_type: str,
        amount,
        currency,
        exchange_currency,
        exchange_rate,
        transaction_fee
    ) -> AccountCurrencyTransaction:
        account_currency_transaction = AccountCurrencyTransaction.objects.create(
            sender_account=sender_account,
            receiver_account=receiver_account,
            transaction_type=transaction_type,
            amount=amount,
            currency=currency,
            exchange_currency=exchange_currency,
            exchange_rate=exchange_rate,
            transaction_fee=transaction_fee
        )
        return account_currency_transaction

    def get_transactions_by_account(self, account_id: int) -> List[AccountCurrencyTransaction]:
        qs1 = AccountCurrencyTransaction.objects.filter(sender_account_id=account_id)
        qs2 = AccountCurrencyTransaction.objects.filter(receiver_account_id=account_id)

        qs_union = qs1.union(qs2).order_by('-transaction_date')

        return list(qs_union)

    def get_transaction_by_id(self, account_currency_transaction_id: int) -> Optional[AccountCurrencyTransaction]:
        return AccountCurrencyTransaction.objects.filter(pk=account_currency_transaction_id).first()

    def delete_transaction(self, account_currency_transaction_id: int) -> bool:
        account_currency_transaction = self.get_transaction_by_id(account_currency_transaction_id)
        if account_currency_transaction:
            account_currency_transaction.delete()
            return True
        return False
