import decimal
from decimal import Decimal, ROUND_DOWN
from typing import Optional, List, Union

from myapp.models.models import AccountCurrencyTransaction, Account
from myapp.utils.util_functions import normalize_decimal


class AccountCurrencyTransactionsRepository:

    def get_account_currency_transactions_by_account(self, account_id: int) -> List[AccountCurrencyTransaction]:
        sent = AccountCurrencyTransaction.objects.filter(sender_account_id=account_id) \
            .select_related('currency', 'sender_account', 'receiver_account')
        received = AccountCurrencyTransaction.objects.filter(receiver_account_id=account_id) \
            .select_related('currency', 'sender_account', 'receiver_account')
        return list(sent.union(received).order_by('-transaction_date'))

    def get_account_currency_transaction_by_id(self, account_currency_transaction_id: int) -> Optional[AccountCurrencyTransaction]:
        return AccountCurrencyTransaction.objects.filter(pk=account_currency_transaction_id).first()


    def create_transaction(
        self,
        sender_account: Optional[Account],
        receiver_account: Account,
        transaction_type: str,
        title: str,
        amount,
        currency,
        exchange_rate,
        transaction_fee,
        default_currency_cost
    ) -> AccountCurrencyTransaction:
        try:
            amount = normalize_decimal(amount)
            transaction_fee = normalize_decimal(transaction_fee)
            default_currency_cost = normalize_decimal(default_currency_cost)
            exchange_rate = normalize_decimal(exchange_rate) if exchange_rate is not None else None

        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            raise ValueError(f"Invalid numeric value provided: {str(e)}")

        if amount <= Decimal('0'):
            raise ValueError("Transaction amount must be positive")
        if transaction_fee < Decimal('0'):
            raise ValueError("Transaction fee cannot be negative")
        if transaction_type == 'deposit':
            sender_account = None
        try:
            account_currency_transaction = AccountCurrencyTransaction(
                sender_account=sender_account, receiver_account=receiver_account,
                transaction_type=transaction_type, title=title, amount=amount,
                currency=currency, exchange_rate=exchange_rate,
                transaction_fee=transaction_fee, default_currency_cost=default_currency_cost)

            account_currency_transaction.full_clean()
            account_currency_transaction.save()
            return account_currency_transaction

        except Exception as e:
            raise ValueError(f"Failed to create transaction: {str(e)}")


    def delete_transaction(self, account_currency_transaction_id: int) -> bool:
        account_currency_transaction = self.get_account_currency_transaction_by_id(account_currency_transaction_id)
        if account_currency_transaction:
            account_currency_transaction.delete()
            return True
        return False
