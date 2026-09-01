from sqlalchemy.orm import Session

import secrets

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.security import InvalidTokenError
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenPair


class AuthError(Exception):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, email: str, password: str, full_name: str | None) -> User:
        if self.users.get_by_email(email) is not None:
            raise AuthError("A user with this email already exists")
        return self.users.create(email, hash_password(password), full_name)

    def login_or_register_oauth_user(self, email: str, full_name: str | None) -> User:
        user = self.users.get_by_email(email)
        if user is not None:
            if not user.is_active:
                raise AuthError("This account has been deactivated")
            return user
        unusable_password = hash_password(secrets.token_urlsafe(32))
        return self.users.create(email, unusable_password, full_name)

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password")
        if not user.is_active:
            raise AuthError("This account has been deactivated")
        return user

    def issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def refresh(self, refresh_token: str) -> TokenPair:
        try:
            user_id = decode_token(refresh_token, expected_type="refresh")
        except InvalidTokenError as exc:
            raise AuthError("Invalid or expired refresh token") from exc

        user = self.users.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthError("Invalid or expired refresh token")

        return self.issue_tokens(user)
