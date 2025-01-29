import uuid
from decimal import Decimal
from math import ceil


from myapp.repositories.account_currency_transactions_repository import AccountCurrencyTransactionsRepository
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository


class AccountsService:
    def __init__(self):
        self.account_currency_repository = AccountCurrenciesRepository()
        self.accounts_repository = AccountsRepository()
        self.currencies_repository = CurrenciesRepository()
        self.account_currency_transactions_repository = AccountCurrencyTransactionsRepository()

    def create_account(self, user_id: int, account_name: str, currency_code: str, balance: float = 0.0):
        account = self.accounts_repository.get_account_by_user_id(user_id)
        if account:
            raise ValueError("Account already exists for this user")

        currency = self.currencies_repository.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} does not exist")

        public_account_id = self.generate_public_account_id(currency_code)

        account = self.accounts_repository.create_account(user_id, account_name, public_account_id, currency.id)

        self.account_currency_repository.create_account_currency(account.id, currency.id, balance)

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




    def get_usd_balance(self, account_id: int) -> Decimal:
        currency = self.currencies_repository.get_currency_by_code("USD")
        if not currency:
            raise ValueError("USD currency not found.")
        ac = self.account_currency_repository.get_account_currency_balance_by_id(account_id, currency.id)
        return ac.balance if ac else Decimal(0)

    def get_account_currency_transactions(self, account_id: int, page: int, page_size: int) -> dict:

        all_transactions = self.account_currency_transactions_repository.get_account_currency_transactions_by_account(account_id)

        total_count = len(all_transactions)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        results = all_transactions[start_index:end_index]

        total_pages = ceil(total_count / page_size)

        transactions_list = []
        for transaction in results:

            transactions_list.append({
                "id": transaction.id,
                "transaction_type": transaction.transaction_type,
                "amount": str(transaction.amount),
                "title": transaction.title,
                "currency": transaction.currency.code,
                "exchange_rate": str(transaction.exchange_rate) if transaction.exchange_rate else None,
                "transaction_fee": str(transaction.transaction_fee),
                "sender_account_id": transaction.sender_account_id,
                "receiver_account_id": transaction.receiver_account_id,
                "date": transaction.transaction_date.isoformat(),
                "default_currency_cost": str(transaction.default_currency_cost)

            })

        return {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count,
            "transactions": transactions_list
        }

    def get_account_stock_transactions(self, account_id: int, page: int, page_size: int) -> dict:
        all_stock_transactions = self.account_stock_transactions_repository.get_stock_transactions_by_account(
            account_id)

        total_count = len(all_stock_transactions)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        results = all_stock_transactions[start_index:end_index]

        total_pages = ceil(total_count / page_size)

        transactions_list = []
        for transaction in results:
            transactions_list.append({
                "id": transaction.id,
                "transaction_type": transaction.transaction_type,
                "shares": str(transaction.shares),
                "title": transaction.title,
                "stock_symbol": transaction.stock.stock_symbol,
                "currency": transaction.currency.code,
                "price_per_share": str(transaction.price_per_share),
                "exchange_rate": str(transaction.exchange_rate) if transaction.exchange_rate else None,
                "transaction_fee": str(transaction.transaction_fee),
                "default_currency_cost": str(transaction.default_currency_cost),
                "transaction_date": transaction.transaction_date.isoformat(),
            })

        return {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count,
            "transactions": transactions_list
        }