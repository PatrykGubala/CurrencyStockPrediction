import base64
import os
import uuid
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from firebase_admin import auth
import firebase_admin

from myapp.models import User
from myapp.repositories.users_repository import UsersRepository
from myapp.services.accounts_service import AccountsService
import logging


logger = logging.getLogger(__name__)

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
            'profile_image_url': user.profile_image_url,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }

    def get_user_by_firebase_uid(self, firebase_uid: str):
        user = self.users_repo.get_user_by_firebase_uid(firebase_uid)
        return user

    def upload_profile_image(self, user, image_base64: str) -> str:
        try:
            if ',' in image_base64:
                header, imgstr = image_base64.split(',', 1)
                format = header.split('/')[-1].split(';')[0]
            else:
                imgstr = image_base64
                format = 'jpg'

            img_data = base64.b64decode(imgstr)
            filename = f"profile_{uuid.uuid4()}.{format}"
            user_folder = os.path.join(settings.MEDIA_ROOT, 'profile_images', str(user.id))
            os.makedirs(user_folder, exist_ok=True)
            file_path = os.path.join(user_folder, filename)

            existing_image_url = user.profile_image_url
            if existing_image_url:
                relative_path = existing_image_url.replace(settings.MEDIA_URL, '')
                existing_file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                if os.path.exists(existing_file_path):
                    os.remove(existing_file_path)
                    logger.info(f"Deleted existing profile image for user {user.id}: {existing_file_path}")

            with open(file_path, 'wb') as f:
                f.write(img_data)
            logger.info(f"Saved new profile image for user {user.id}: {file_path}")

            relative_path = os.path.join('profile_images', str(user.id), filename).replace('\\', '/')
            self.users_repo.update_user_profile_image(user, relative_path)

            full_url = f"{settings.MEDIA_URL}{relative_path}"
            return full_url
        except Exception as e:
            logger.error(f"Error uploading profile image for user {user.id}: {e}")
            raise e



    def change_username(self, user: User, new_username: str):
        if self.users_repo.get_user_by_username(new_username):
            raise ValueError("Username already in use")
        self.users_repo.update_username(user, new_username)
        logger.info(f"User {user.id} changed username to {new_username}")

    def initiate_change_email(self, user: User, new_email: str):
        if self.users_repo.get_user_by_email(new_email):
            raise ValueError("Email already in use")

        try:
            token = jwt.encode({
                'user_id': user.id,
                'new_email': new_email,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }, settings.SECRET_KEY, algorithm='HS256')

            verification_link = f"{settings.BACKEND_URL}/myapp/users/verify_change_email?token={token}"
            logger.info(f"Verification link generated: {verification_link}")
            self.send_verification_email(new_email, verification_link)

        except Exception as e:
            logger.error(f"Error initiating email change: {e}")
            raise ValueError("Failed to initiate email change")

    def verify_change_email(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            new_email = payload.get('new_email')

            if not user_id or not new_email:
                raise ValueError("Invalid token payload")

            user = self.users_repo.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            if self.users_repo.get_user_by_email(new_email):
                raise ValueError("Email already in use")

            with transaction.atomic():
                auth.update_user(
                    user.firebase_uid,
                    email=new_email,
                    email_verified=False
                )

                user.email = new_email
                user.save()

            return new_email
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            logger.error("Invalid token")
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Error verifying email change: {e}")
            raise ValueError("Failed to verify email change")

    def send_verification_email(self, email: str, link: str):
        subject = "Verify Your New Email Address"
        message = f"Please verify your new email address by clicking on the following link:\n\n{link}\n\nIf you did not request this change, please contact support immediately."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            logger.info(f"Verification email sent to {email}")
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {e}")
            raise



