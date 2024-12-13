from django.db import transaction
from firebase_admin import auth
import firebase_admin
from myapp.repositories.users_repository import UsersRepository
from myapp.services.accounts_service import AccountsService

class UsersService:
    def __init__(self):
        self.users_repo = UsersRepository()
        self.accounts_service = AccountsService()

    def register_user(self, data: dict):
        firebase_uid = data.get('firebase_uid')
        email = data.get('email', '').strip().lower()
        username = data.get('username', '').strip()

        if not firebase_uid or not email or not username:
            raise ValueError('Firebase UID, email, and username are required')

        if self.users_repo.get_user_by_firebase_uid(firebase_uid):
            raise ValueError("User already exists")
        if self.users_repo.get_user_by_email(email):
            raise ValueError("Email already in use")
        if self.users_repo.get_user_by_username(username):
            raise ValueError("Username already in use")

        try:
            with transaction.atomic():
                user = self.users_repo.add_user(firebase_uid, email, username)
                self.accounts_service.create_default_account(user.id)
        except Exception as e:
            try:
                auth.delete_user(firebase_uid)
            except firebase_admin.auth.UserNotFoundError:
                pass
            raise e

    def get_user_by_id_dto(self, user_id: int):
        user = self.users_repo.get_user_by_id(user_id)
        if not user:
            return None
        return {
            'id': user.id,
            'firebase_uid': user.firebase_uid,
            'email': user.email,
            'username': user.username,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }

    def get_user_by_firebase_uid(self, firebase_uid: str):
        user = self.users_repo.get_user_by_firebase_uid(firebase_uid)
        return user
