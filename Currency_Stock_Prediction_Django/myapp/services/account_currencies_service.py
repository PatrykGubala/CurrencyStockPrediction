import logging
from decimal import Decimal, ROUND_DOWN
from typing import List, Optional, Union
import re

from django.db import transaction

from myapp.apps import logger
from myapp.repositories.account_currencies_repository import AccountCurrenciesRepository
from myapp.repositories.account_currency_transactions_repository import AccountCurrencyTransactionsRepository
from myapp.repositories.accounts_repository import AccountsRepository
from myapp.repositories.currencies_repository import CurrenciesRepository
from myapp.utils.util_functions import normalize_decimal


class AccountCurrenciesService:
    FEE_RATE = Decimal('0.005')

    def __init__(self):
        self.account_currency_repository = AccountCurrenciesRepository()
        self.accounts_repository = AccountsRepository()
        self.currencies_repository = CurrenciesRepository()
        self.account_currency_transactions_repository = AccountCurrencyTransactionsRepository()


    def get_account_currencies(self, account_id: int) -> List[dict]:
        account_currencies = self.account_currency_repository.get_all_account_currencies(account_id)
        result = []
        for ac in account_currencies:
            result.append({
                'currency_code': ac.currency.code,
                'balance': float(ac.balance)
            })
        return result

    def get_single_account_currency_balance(self, account_id: int, currency_code: str) -> dict:
        currency = self.currencies_repository.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} not found")
        account = self.account_currency_repository.get_account_currency_balance_by_id(account_id, currency.id)
        balance = account.balance if account else Decimal(0)
        return {
            "currency_code": currency.code,
            "balance": str(balance)
        }

    def add_currency_to_account(self, account_id: int, currency_code: str, balance: float = 0.0):
        account = self.accounts_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} does not exist")
        currency = self.accounts_repository.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} does not exist")
        existing_account_currency = self.account_currency_repository.get_account_currency_balance_by_id(account_id,
                                                                                                  currency.id)
        if existing_account_currency:
            raise ValueError(f"Currency {currency_code} already added to account")
        account = self.account_currency_repository.create_account_currency(account_id, currency.id, balance)
        return {
            'account_id': account.account_id,
            'currency_code': currency.code,
            'balance': float(account.balance)
        }

    def update_balance(self, account_id: int, currency_code: str, balance: float):
        currency = self.currencies_repository.get_currency_by_code(currency_code)
        if not currency:
            raise ValueError(f"Currency with code {currency_code} not found")
        account = self.account_currency_repository.update_account_currency_balance(account_id, currency.id, balance)
        if not account:
            raise ValueError(f"Currency {currency_code} not associated with account {account_id}")
        return {
            'currency_code': currency.code,
            'balance': float(account.balance)
        }

    def deposit_to_usd_account(self, account_id: int, amount: Union[str, float, Decimal]) -> Optional[dict]:
        try:
            normalized_amount = normalize_decimal(amount)
            if normalized_amount <= 0:
                raise ValueError("Deposit amount must be positive.")

            usd_currency = self.currencies_repository.get_currency_by_code("USD")
            if not usd_currency:
                raise ValueError("USD currency not found.")

            account_currency = self.account_currency_repository.get_account_currency_balance_by_id(account_id,
                                                                                                   usd_currency.id)
            if not account_currency:
                raise ValueError("USD account currency not found.")

            current_balance = normalize_decimal(account_currency.balance)
            new_balance = current_balance + normalized_amount

            with transaction.atomic():
                self.account_currency_repository.update_account_currency_balance(
                    account_id,
                    usd_currency.id,
                    new_balance
                )

                self.account_currency_transactions_repository.create_transaction(
                    sender_account=None,
                    receiver_account=account_currency.account,
                    transaction_type='deposit',
                    title='Wpływ USD',
                    amount=normalized_amount,
                    currency=usd_currency,
                    exchange_rate=None,
                    transaction_fee=normalize_decimal("0"),
                    default_currency_cost=normalized_amount
                )

            return {
                "currency_code": "USD",
                "new_balance": float(new_balance)
            }
        except Exception as e:
            logger.error(f"Error in deposit_to_usd_account: {e}")
            return None

    def buy_currency(self, account_id: int, currency_code: str, amount: Union[str, float, Decimal]):
        normalized_amount = normalize_decimal(amount)
        if normalized_amount <= 0:
            raise ValueError("Amount must be positive.")

        target_currency = self.currencies_repository.get_currency_by_code(currency_code)
        if not target_currency:
            raise ValueError(f"Currency {currency_code} does not exist")

        usd_currency = self.currencies_repository.get_currency_by_code("USD")
        if not usd_currency:
            raise ValueError("USD currency not found")

        usd_account = self.account_currency_repository.get_account_currency_balance_by_id(
            account_id, usd_currency.id
        )
        if not usd_account:
            raise ValueError("USD balance not found for this account")

        latest_currency_data = self.currencies_repository.get_latest_currency_data(currency_code)
        if not latest_currency_data:
            raise ValueError("No currency data available to determine price")

        close_price = normalize_decimal(latest_currency_data.close_price)
        usd_per_unit = Decimal('1.0') / close_price

        base_cost = normalized_amount * usd_per_unit
        transaction_fee = normalize_decimal(base_cost * self.FEE_RATE)
        total_cost = base_cost + transaction_fee

        current_usd_balance = normalize_decimal(usd_account.balance)
        if current_usd_balance < total_cost:
            raise ValueError("Insufficient USD balance")

        with transaction.atomic():
            new_usd_balance = current_usd_balance - total_cost
            self.account_currency_repository.update_account_currency_balance(
                account_id,
                usd_currency.id,
                new_usd_balance
            )

            target_currency_account = self.account_currency_repository.get_account_currency_balance_by_id(
                account_id, target_currency.id
            )

            if not target_currency_account:
                self.account_currency_repository.create_account_currency(
                    account_id, target_currency.id, normalized_amount
                )
            else:
                current_target_balance = normalize_decimal(target_currency_account.balance)
                new_target_balance = current_target_balance + normalized_amount
                self.account_currency_repository.update_account_currency_balance(
                    account_id,
                    target_currency.id,
                    new_target_balance
                )

            self.account_currency_transactions_repository.create_transaction(
                sender_account=usd_account.account,
                receiver_account=usd_account.account,
                transaction_type='buy',
                title=f'Zakupiono {currency_code}',
                amount=normalized_amount,
                currency=target_currency,
                exchange_rate=usd_per_unit,
                transaction_fee=transaction_fee,
                default_currency_cost=total_cost
            )

        return True

    def sell_currency(self, account_id: int, currency_code: str, amount: Union[str, float, Decimal]):
        normalized_amount = normalize_decimal(amount)
        logger.error(f"sell_currency called with normalized_amount={normalized_amount}")
        if normalized_amount <= Decimal('0'):
            raise ValueError("Amount must be positive.")

        source_currency = self.currencies_repository.get_currency_by_code(currency_code)
        if not source_currency:
            raise ValueError(f"Currency {currency_code} does not exist")

        usd_currency = self.currencies_repository.get_currency_by_code("USD")
        if not usd_currency:
            raise ValueError("USD currency not found")

        source_account = self.account_currency_repository.get_account_currency_balance_by_id(
            account_id, source_currency.id
        )
        if not source_account:
            raise ValueError(f"Insufficient {currency_code} balance")

        current_source_balance = normalize_decimal(source_account.balance)
        logger.error(f"sell_currency current_source_balance={current_source_balance}")
        if current_source_balance < normalized_amount:
            raise ValueError(f"Insufficient {currency_code} balance to sell")

        latest_currency_data = self.currencies_repository.get_latest_currency_data(currency_code)
        if not latest_currency_data:
            raise ValueError("No currency data available to determine price")

        close_price = normalize_decimal(latest_currency_data.close_price)
        logger.error(f"sell_currency close_price={close_price}")
        usd_per_unit = Decimal('1.0') / close_price
        logger.error(f"sell_currency usd_per_unit={usd_per_unit}")

        base_revenue = normalized_amount * usd_per_unit
        logger.error(f"sell_currency base_revenue={base_revenue}")
        transaction_fee = normalize_decimal(base_revenue * self.FEE_RATE)
        logger.error(f"sell_currency transaction_fee={transaction_fee}")
        total_revenue = base_revenue - transaction_fee
        logger.error(f"sell_currency total_revenue={total_revenue}")

        usd_account = self.account_currency_repository.get_account_currency_balance_by_id(
            account_id, usd_currency.id
        )
        if not usd_account:
            raise ValueError("USD account not found")

        current_usd_balance = normalize_decimal(usd_account.balance)
        logger.error(f"sell_currency current_usd_balance={current_usd_balance}")

        with transaction.atomic():
            new_source_balance = current_source_balance - normalized_amount
            logger.error(f"sell_currency new_source_balance={new_source_balance}")
            self.account_currency_repository.update_account_currency_balance(
                account_id, source_currency.id, new_source_balance
            )

            new_usd_balance = current_usd_balance + total_revenue
            logger.error(f"sell_currency new_usd_balance={new_usd_balance}")
            self.account_currency_repository.update_account_currency_balance(
                account_id, usd_currency.id, new_usd_balance
            )

            self.account_currency_transactions_repository.create_transaction(
                sender_account=usd_account.account,
                receiver_account=usd_account.account,
                transaction_type='sell',
                title=f'Sprzedano {currency_code}',
                amount=normalized_amount,
                currency=source_currency,
                exchange_rate=usd_per_unit,
                transaction_fee=transaction_fee,
                default_currency_cost=total_revenue
            )

        return True

    def send_currency(self, sender_account_id: int, receiver_public_account_id: str,
                      amount: Union[str, float, Decimal]) -> Optional[dict]:
        normalized_amount = normalize_decimal(amount)
        if normalized_amount <= Decimal('0'):
            raise ValueError("Amount must be positive.")

        usd_currency = self.currencies_repository.get_currency_by_code("USD")
        if not usd_currency:
            raise ValueError("USD currency not found.")

        sender_account = self.account_currency_repository.get_account_currency_balance_by_id(
            sender_account_id, usd_currency.id
        )
        if not sender_account:
            raise ValueError("Sender's USD account not found.")

        sender_balance = normalize_decimal(sender_account.balance)
        if sender_balance < normalized_amount:
            raise ValueError("Insufficient USD balance.")

        if not self.validate_public_account_id(receiver_public_account_id):
            raise ValueError("Invalid Public Account ID format.")

        receiver_account = self.accounts_repository.get_account_by_public_id(receiver_public_account_id)
        if not receiver_account:
            raise ValueError("Receiver account not found.")

        receiver_usd_account = self.account_currency_repository.get_account_currency_balance_by_id(
            receiver_account.id, usd_currency.id
        )
        if not receiver_usd_account:
            receiver_usd_account = self.account_currency_repository.create_account_currency(
                receiver_account.id, usd_currency.id, 0
            )

        with transaction.atomic():
            new_sender_balance = sender_balance - normalized_amount
            self.account_currency_repository.update_account_currency_balance(
                sender_account_id, usd_currency.id, new_sender_balance
            )

            receiver_balance = normalize_decimal(receiver_usd_account.balance)
            new_receiver_balance = receiver_balance + normalized_amount
            self.account_currency_repository.update_account_currency_balance(
                receiver_account.id, usd_currency.id, new_receiver_balance
            )

            self.account_currency_transactions_repository.create_transaction(
                sender_account=sender_account.account,
                receiver_account=receiver_usd_account.account,
                transaction_type='send',
                title='Wysyłka USD',
                amount=normalized_amount,
                currency=usd_currency,
                exchange_rate=None,
                transaction_fee=normalize_decimal("0"),
                default_currency_cost=normalized_amount
            )

        return {
            "message": "Transfer successful",
            "sender_new_balance": float(new_sender_balance),
            "receiver_new_balance": float(new_receiver_balance)
        }

    @staticmethod
    def validate_public_account_id(public_account_id: str) -> bool:
        pattern = re.compile(r'^[a-fA-F0-9]{13}[A-Z]{3}$')
        return bool(pattern.match(public_account_id))