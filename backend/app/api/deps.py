"""Shared FastAPI dependencies."""

import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.errors import ApiError
from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

LOCAL_USER_EMAIL = "local@ragnarock.local"


def _local_user(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == LOCAL_USER_EMAIL))
    if user is not None:
        return user

    user = User(email=LOCAL_USER_EMAIL, password_hash="!")
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        user = db.scalar(select(User).where(User.email == LOCAL_USER_EMAIL))
        if user is None:
            raise
        return user
    db.refresh(user)
    return user


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    settings = get_settings()
    if settings.auth_disabled:
        return _local_user(db)

    if not authorization or not authorization.lower().startswith("bearer "):
        raise ApiError(401, "not_authenticated", "A bearer access token is required.")

    token = authorization.split(" ", 1)[1].strip()
    subject = decode_access_token(token)
    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise ApiError(401, "invalid_token", "The access token subject is invalid.") from exc

    user = db.get(User, user_id)
    if user is None:
        raise ApiError(401, "invalid_token", "The access token user no longer exists.")
    return user
