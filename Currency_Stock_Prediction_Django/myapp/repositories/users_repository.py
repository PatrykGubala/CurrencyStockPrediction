from typing import Optional
from myapp.models import User

class UsersRepository:
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def get_user_by_firebase_uid(self, firebase_uid: str) -> Optional[User]:
        return User.objects.filter(firebase_uid=firebase_uid).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return User.objects.filter(email=email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return User.objects.filter(username=username).first()

    def add_user(self, firebase_uid: str, email: str, username: str) -> User:
        user = User(firebase_uid=firebase_uid, email=email, username=username)
        user.save()
        return user

    def update_user_profile_image(self, user: User, image_url: str):
        user.profile_image_url = image_url
        user.save()

    def update_username(self, user: User, new_username: str):
        user.username = new_username
        user.save()