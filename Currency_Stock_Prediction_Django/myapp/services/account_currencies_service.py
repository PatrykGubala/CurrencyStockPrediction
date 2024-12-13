from typing import List
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository

class AccountCurrenciesService:
    def __init__(self):
        self.account_currency_repo = AccountCurrenciesRepository()
        self.accounts_repo = AccountsRepository()
        self.currencies_repo = CurrenciesRepository()

    def add_currency_to_account(self, account_id: int, currency_code: str, balance: float = 0.0):
        account = self.accounts_repo.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} does not exist")
        currency = self.currencies_repo.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} does not exist")
        existing_account_currency = self.account_currency_repo.get_by_account_and_currency(account_id, currency.id)
        if existing_account_currency:
            raise ValueError(f"Currency {currency_code} already added to account")
        ac = self.account_currency_repo.add_account_currency(account_id, currency.id, balance)
        return {
            'account_id': ac.account_id,
            'currency_code': currency.code,
            'balance': float(ac.balance)
        }

    def get_account_currencies(self, account_id: int) -> List[dict]:
        account_currencies = self.account_currency_repo.get_account_currencies(account_id)
        result = []
        for ac in account_currencies:
            result.append({
                'currency_code': ac.currency.code,
                'balance': float(ac.balance)
            })
        return result

    def update_balance(self, account_id: int, currency_code: str, balance: float):
        currency = self.currencies_repo.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} not found")
        ac = self.account_currency_repo.update_balance(account_id, currency.id, balance)
        if not ac:
            raise ValueError(f"Currency {currency_code} not associated with account {account_id}")
        return {
            'currency_code': currency.code,
            'balance': float(ac.balance)
        }

    def remove_currency_from_account(self, account_id: int, currency_code: str):
        currency = self.currencies_repo.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} not found")
        result = self.account_currency_repo.delete_account_currency(account_id, currency.id)
        if not result:
            raise ValueError(f"Currency {currency_code} not associated with account {account_id}")
        return True
