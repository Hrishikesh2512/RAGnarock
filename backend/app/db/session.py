"""Synchronous SQLAlchemy engine and request-scoped sessions."""

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _create_engine() -> Engine:
    return create_engine(
        get_settings().database_url,
        pool_pre_ping=True,
        future=True,
    )


engine = _create_engine()

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a session and closing it afterwards."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
