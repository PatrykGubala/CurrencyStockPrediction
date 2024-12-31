from decimal import Decimal
from typing import List, Optional
import re

from django.db import transaction
from django.utils import timezone

from myapp.apps import logger
from myapp.models.models import AccountCurrencyValueHistory
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository
from myapp.repositories.account_currency_transactions_repository import AccountCurrencyTransactionsRepository
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository

class AccountCurrenciesService:
    def __init__(self):
        self.account_currency_repo = AccountCurrenciesRepository()
        self.accounts_repo = AccountsRepository()
        self.currencies_repo = CurrenciesRepository()
        self.account_currency_tx_repo = AccountCurrencyTransactionsRepository()

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

    def get_single_account_currency_balance(self, account_id: int, currency_code: str) -> dict:
        currency = self.currencies_repo.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} not found")
        ac = self.account_currency_repo.get_by_account_and_currency(account_id, currency.id)
        balance = ac.balance if ac else Decimal(0)
        return {
            "currency_code": currency.code,
            "balance": str(balance)
        }

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

    def record_currency_value(self, account_currency):
        latest_currency_data = self.currencies_repo.get_latest_currency_data(account_currency.currency.code)
        if latest_currency_data:
            balance_usd = Decimal(account_currency.balance) * Decimal(latest_currency_data.close_price)
            AccountCurrencyValueHistory.objects.create(
                account_currency=account_currency,
                balance_usd=balance_usd,
                timestamp=timezone.now()
            )

    def record_currency_deletion(self, account_currency):
        latest_currency_data = self.currencies_repo.get_latest_currency_data(account_currency.currency.code)
        if latest_currency_data:
            balance_usd = Decimal(account_currency.balance) * Decimal(latest_currency_data.close_price)
            AccountCurrencyValueHistory.objects.create(
                account_currency=account_currency,
                balance_usd=balance_usd,
                timestamp=timezone.now()
            )

    def deposit_to_usd_account(self, account_id: int, amount: float) -> Optional[dict]:
        try:
            if amount <= 0:
                raise ValueError("Deposit amount must be positive.")
            currency = self.currencies_repo.get_currency_by_code("USD")
            if not currency:
                raise ValueError("USD currency not found.")
            account_currency = self.account_currency_repo.get_by_account_and_currency(account_id, currency.id)
            if not account_currency:
                raise ValueError("USD account currency not found.")
            new_balance = Decimal(account_currency.balance) + Decimal(amount)

            with transaction.atomic():
                self.account_currency_repo.update_balance(account_id, currency.id, float(new_balance))

                AccountCurrencyValueHistory.objects.create(
                    account_currency=account_currency,
                    balance_usd=new_balance,
                    timestamp=timezone.now()
                )

                self.account_currency_tx_repo.create_transaction(
                    sender_account=None,
                    receiver_account=account_currency.account,
                    transaction_type='deposit',
                    amount=Decimal(amount),
                    currency=currency,
                    exchange_currency=None,
                    exchange_rate=None,
                    transaction_fee=Decimal('0.00')
                )

            return {
                "currency_code": "USD",
                "new_balance": float(new_balance)
            }
        except Exception as e:
            logger.error(f"Error in deposit_to_usd_account: {e}")
            return None

    def buy_currency(self, account_id: int, currency_code: str, amount: float):
        if amount <= 0:
            raise ValueError("Amount must be positive.")

        currency = self.currencies_repo.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency {currency_code} does not exist")

        usd_currency = self.currencies_repo.get_currency_by_code("USD")
        if not usd_currency:
            raise ValueError("USD currency not found")

        account_currency_usd = self.account_currency_repo.get_by_account_and_currency(account_id, usd_currency.id)
        if not account_currency_usd:
            raise ValueError("USD balance not found for this account")

        latest_data = self.currencies_repo.get_latest_currency_data(currency_code)
        if not latest_data:
            raise ValueError("No currency data to determine price")


        close_price_numeric = Decimal(latest_data.close_price)
        price_per_unit_in_usd = Decimal("1") / close_price_numeric

        cost_without_fee = price_per_unit_in_usd * Decimal(amount)
        fee = cost_without_fee * Decimal("0.005")
        total_cost = cost_without_fee + fee

        if account_currency_usd.balance < total_cost:
            raise ValueError("Not enough USD balance")

        with transaction.atomic():
            new_usd_balance = account_currency_usd.balance - total_cost
            self.account_currency_repo.update_balance(account_id, usd_currency.id, float(new_usd_balance))


            existing_currency = self.account_currency_repo.get_by_account_and_currency(account_id, currency.id)
            if not existing_currency:
                self.account_currency_repo.add_account_currency(account_id, currency.id, float(amount))
            else:
                new_balance = existing_currency.balance + Decimal(amount)
                self.account_currency_repo.update_balance(account_id, currency.id, float(new_balance))


            self.account_currency_tx_repo.create_transaction(
                sender_account=account_currency_usd.account,
                receiver_account=account_currency_usd.account,
                transaction_type='exchange',
                amount=Decimal(amount),
                currency=currency,
                exchange_currency=usd_currency,
                exchange_rate=price_per_unit_in_usd,
                transaction_fee=fee
            )

        return True


    def send_currency(self, sender_account_id: int, receiver_public_account_id: str, amount: float) -> Optional[dict]:

            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            usd_currency = self.currencies_repo.get_currency_by_code("USD")
            if not usd_currency:
                raise ValueError("USD currency not found.")

            sender_usd_account = self.account_currency_repo.get_by_account_and_currency(sender_account_id, usd_currency.id)
            if not sender_usd_account:
                raise ValueError("Sender does not have a USD account.")

            if sender_usd_account.balance < Decimal(amount):
                raise ValueError("Insufficient USD balance.")

            if not self.validate_public_account_id(receiver_public_account_id):
                raise ValueError("Invalid Public Account ID format.")

            receiver_account = self.accounts_repo.get_account_by_public_id(receiver_public_account_id)
            if not receiver_account:
                raise ValueError("Receiver account not found.")

            receiver_usd_account = self.account_currency_repo.get_by_account_and_currency(receiver_account.id, usd_currency.id)
            if not receiver_usd_account:
                receiver_usd_account = self.account_currency_repo.add_account_currency(receiver_account.id, usd_currency.id, 0.0)

            with transaction.atomic():
                new_sender_balance = sender_usd_account.balance - Decimal(amount)
                self.account_currency_repo.update_balance(sender_account_id, usd_currency.id, float(new_sender_balance))

                new_receiver_balance = receiver_usd_account.balance + Decimal(amount)
                self.account_currency_repo.update_balance(receiver_account.id, usd_currency.id, float(new_receiver_balance))

                self.account_currency_tx_repo.create_transaction(
                    sender_account=sender_usd_account.account,
                    receiver_account=receiver_usd_account.account,
                    #TODO: CHANGE WITHDRAW TO SEND
                    transaction_type='withdraw',
                    amount=Decimal(amount),
                    currency=usd_currency,
                    exchange_currency=None,
                    exchange_rate=None,
                    transaction_fee=Decimal('0.00')
                )

            return {
                "message": "Send successful.",
                "sender_new_balance": float(new_sender_balance),
                "receiver_new_balance": float(new_receiver_balance)
            }



    @staticmethod
    def validate_public_account_id(public_account_id: str) -> bool:
        pattern = re.compile(r'^[a-fA-F0-9]{13}[A-Z]{3}$')
        return bool(pattern.match(public_account_id))