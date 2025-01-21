from decimal import Decimal, ROUND_DOWN
from typing import Optional, List, Union

from myapp.models import AccountCurrency
from myapp.utils.util_functions import normalize_decimal


class AccountCurrenciesRepository:

    def get_account_currency_balance_by_id(self, account_id: int, currency_id: int) -> Optional[AccountCurrency]:
        return AccountCurrency.objects.filter(account_id=account_id, currency_id=currency_id).first()

    def get_all_account_currencies(self, account_id: int) -> List[AccountCurrency]:
        return list(AccountCurrency.objects.filter(account_id=account_id))

    def create_account_currency(self, account_id: int, currency_id: int, balance: float = 0.0) -> AccountCurrency:
        try:
            balance = normalize_decimal(balance)
            if balance < Decimal('0'):
                raise ValueError("Initial balance cannot be negative")

            account_currency = AccountCurrency(
                account_id=account_id,
                currency_id=currency_id,
                balance=balance
            )
            account_currency.full_clean()
            account_currency.save()
            return account_currency

        except Exception as e:
            raise ValueError(f"Failed to create account currency: {str(e)}")

    def update_account_currency_balance(self, account_id: int, currency_id: int, new_balance: float) -> Optional[AccountCurrency]:
        new_balance = normalize_decimal(new_balance)
        if new_balance < 0:
            raise ValueError("Balance cannot be negative")
        account_currency = self.get_account_currency_balance_by_id(account_id, currency_id)
        if account_currency:
            account_currency.balance = new_balance
            account_currency.full_clean()
            account_currency.save()
        return account_currency

    def delete_account_currency(self, account_id: int, currency_id: int) -> bool:
        account_currency = self.get_account_currency_balance_by_id(account_id, currency_id)
        if account_currency:
            account_currency.delete()
            return True
        return False