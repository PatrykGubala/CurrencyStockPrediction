import uuid
from django.db import transaction, IntegrityError
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository


class AccountsService:
    def __init__(self):
        self.account_currency_repo = AccountCurrenciesRepository()
        self.accounts_repo = AccountsRepository()
        self.currencies_repo = CurrenciesRepository()

    def create_account(self, user_id: int, account_name: str, currency_code: str, balance: float = 0.0):
        account = self.accounts_repo.get_account_by_user_id(user_id)
        if account:
            raise ValueError("Account already exists for this user")

        currency = self.currencies_repo.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} does not exist")

        public_account_id = self.generate_public_account_id(currency_code)

        account = self.accounts_repo.add_account(user_id, account_name, public_account_id, currency.id)

        self.account_currency_repo.add_account_currency(account.id, currency.id, balance)

        return {
            'id': account.id,
            'account_name': account.account_name,
            'public_account_id': account.public_account_id,
            'currency_code': currency.code,
            'balance': float(balance)
        }

    def create_default_account(self, user_id: int):
        default_currency_code = 'USD'
        default_account_name = 'Default Account'
        default_balance = 0.0

        return self.create_account(user_id, default_account_name, default_currency_code, default_balance)

    def generate_public_account_id(self, currency_code: str) -> str:
        uuid_part = uuid.uuid4().hex[:12]
        currency_code_part = currency_code[-4:].zfill(4)
        return f"{uuid_part}{currency_code_part.upper()}"