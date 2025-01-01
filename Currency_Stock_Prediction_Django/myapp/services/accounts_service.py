import uuid
from decimal import Decimal
from math import ceil

from django.db import transaction, IntegrityError
from django.utils import timezone

from myapp.apps import logger
from myapp.models.models import AccountCurrencyValueHistory
from myapp.repositories.account_currency_transactions_repository import AccountCurrencyTransactionsRepository
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository


class AccountsService:
    def __init__(self):
        self.account_currency_repo = AccountCurrenciesRepository()
        self.accounts_repo = AccountsRepository()
        self.currencies_repo = CurrenciesRepository()
        self.account_currency_transactions_repo = AccountCurrencyTransactionsRepository()

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

    def record_currency_value(self, account_currency):
        latest_currency_data = self.currencies_repo.get_latest_currency_data(account_currency.currency.code)
        if latest_currency_data:
            balance_usd = Decimal(account_currency.balance) * Decimal(latest_currency_data.close_price)
            AccountCurrencyValueHistory.objects.create(
                account_currency=account_currency,
                balance_usd=balance_usd,
                timestamp=timezone.now()
            )

    def recount_currency_values(self):
        accounts = self.accounts_repo.get_all_accounts()
        logger.info(f"Found {len(accounts)} accounts.")
        for account in accounts:
            logger.info(f"Processing Account ID: {account.id}")
            account_currencies = self.account_currency_repo.get_account_currencies(account.id)
            logger.info(f" - Found {len(account_currencies)} currencies for Account ID: {account.id}")
            for ac in account_currencies:
                logger.info(f" -- Processing Currency: {ac.currency.code}")
                latest_currency_data = self.currencies_repo.get_latest_currency_data(ac.currency.code)
                if latest_currency_data:
                    balance_usd = Decimal(ac.balance) * Decimal(latest_currency_data.close_price)
                    AccountCurrencyValueHistory.objects.create(
                        account_currency=ac,
                        balance_usd=balance_usd,
                        timestamp=timezone.now()
                    )
                    logger.info(f" --- Recorded USD Balance: {balance_usd}")
                else:
                    logger.warning(f" --- No latest currency data for {ac.currency.code}")

    def get_usd_balance(self, account_id: int) -> Decimal:
        currency = self.currencies_repo.get_currency_by_code("USD")
        if not currency:
            raise ValueError("USD currency not found.")
        ac = self.account_currency_repo.get_by_account_and_currency(account_id, currency.id)
        return ac.balance if ac else Decimal(0)

    def get_account_transactions(self, account_id: int, page: int, page_size: int) -> dict:

        all_transactions = self.account_currency_transactions_repo.get_transactions_by_account(account_id)

        total_count = len(all_transactions)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        results = all_transactions[start_index:end_index]

        total_pages = ceil(total_count / page_size)

        transactions_list = []
        for tx in results:
            transactions_list.append({
                "id": tx.id,
                "transaction_type": tx.transaction_type,
                "amount": str(tx.amount),
                "title": tx.title,
                "currency": tx.currency.code,
                "exchange_currency": tx.exchange_currency.code if tx.exchange_currency else None,
                "exchange_rate": str(tx.exchange_rate) if tx.exchange_rate else None,
                "transaction_fee": str(tx.transaction_fee),
                "sender_account_id": tx.sender_account_id,
                "receiver_account_id": tx.receiver_account_id,
                "date": tx.transaction_date.isoformat()
            })

        return {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "total_count": total_count,
            "transactions": transactions_list
        }