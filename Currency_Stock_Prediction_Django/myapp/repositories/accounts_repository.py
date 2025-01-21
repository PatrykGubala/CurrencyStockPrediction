from typing import Optional, List


from myapp.models.models import Account

class AccountsRepository:
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        try:
            return Account.objects.get(pk=account_id)
        except Account.DoesNotExist:
            return None

    def get_account_by_user_id(self, user_id: int) -> Optional[Account]:
        return Account.objects.filter(user_id=user_id).first()

    def get_account_by_public_id(self, public_account_id: str) -> Optional[Account]:
        return Account.objects.filter(public_account_id=public_account_id).first()

    def get_all_accounts(self) -> List[Account]:
        return list(Account.objects.all())

    def create_account(self, user_id: int, account_name: str, public_account_id: str, currency_id: int) -> Account:
        account = Account(user_id=user_id, account_name=account_name, public_account_id=public_account_id,
                          currency_id=currency_id)
        account.save()
        return account
