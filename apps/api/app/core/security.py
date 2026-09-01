from datetime import datetime, timedelta, timezone
from typing import Any, Literal
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(subject: UUID, token_type: TokenType, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: UUID) -> str:
    settings = get_settings()
    return _create_token(
        subject, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(subject: UUID) -> str:
    settings = get_settings()
    return _create_token(
        subject, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


class InvalidTokenError(Exception):
    pass


def decode_token(token: str, expected_type: TokenType) -> UUID:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise InvalidTokenError("Token could not be decoded") from exc

    if payload.get("type") != expected_type:
        raise InvalidTokenError(f"Expected token type '{expected_type}'")

    subject = payload.get("sub")
    if subject is None:
        raise InvalidTokenError("Token missing subject")

    return UUID(subject)
