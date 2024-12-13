from typing import Optional, List
from myapp.models import AccountCurrency

class AccountCurrenciesRepository:
    def get_by_account_and_currency(self, account_id: int, currency_id: int) -> Optional[AccountCurrency]:
        return AccountCurrency.objects.filter(account_id=account_id, currency_id=currency_id).first()

    def add_account_currency(self, account_id: int, currency_id: int, balance: float) -> AccountCurrency:
        account_currency = AccountCurrency(account_id=account_id, currency_id=currency_id, balance=balance)
        account_currency.save()
        return account_currency

    def get_account_currencies(self, account_id: int) -> List[AccountCurrency]:
        return list(AccountCurrency.objects.filter(account_id=account_id))

    def update_balance(self, account_id: int, currency_id: int, balance: float) -> Optional[AccountCurrency]:
        account_currency = self.get_by_account_and_currency(account_id, currency_id)
        if account_currency:
            account_currency.balance = balance
            account_currency.save()
        return account_currency

    def delete_account_currency(self, account_id: int, currency_id: int) -> bool:
        account_currency = self.get_by_account_and_currency(account_id, currency_id)
        if account_currency:
            account_currency.delete()
            return True
        return False