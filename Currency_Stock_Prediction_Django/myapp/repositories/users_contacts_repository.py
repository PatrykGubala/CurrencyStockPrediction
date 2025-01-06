from typing import List, Optional
from myapp.models import Contact, Account


class UsersContactsRepository:

    def get_contacts_by_user(self, user) -> List[Contact]:
        return list(Contact.objects.filter(user=user))

    def add_contact(self, user, title: str, public_account_id: str, account_name: str, currency_code: str) -> Contact:
        contact = Contact.objects.create(
            user=user,
            title=title,
            public_account_id=public_account_id,
            account_name=account_name,
            currency_code=currency_code
        )
        return contact

    def account_exists(self, public_account_id: str) -> bool:
        return Account.objects.filter(public_account_id=public_account_id).exists()