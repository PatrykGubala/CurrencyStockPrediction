from myapp.repositories.users_contacts_repository import UsersContactsRepository

class UsersContactsService:
    def __init__(self):
        self.contacts_repo = UsersContactsRepository()

    def list_contacts(self, user):
        return self.contacts_repo.get_contacts_by_user(user)

    def create_contact(self, user, title: str, public_account_id: str, account_name: str):
        if not self.contacts_repo.account_exists(public_account_id):
            raise ValueError("Public account ID does not exist.")
        return self.contacts_repo.add_contact(user, title, public_account_id, account_name)