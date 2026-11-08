"""Password hashing and access-token helpers."""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

from app.api.errors import ApiError
from app.core.config import get_settings

_hasher = PasswordHasher()
_JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def _jwt_secret() -> str:
    secret = get_settings().jwt_secret
    if not secret:
        raise ApiError(500, "auth_misconfigured", "JWT_SECRET is not configured.")
    return secret


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=_JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[_JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise ApiError(401, "invalid_token", "The access token is invalid or expired.") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str):
        raise ApiError(401, "invalid_token", "The access token has no subject.")
    return subject
