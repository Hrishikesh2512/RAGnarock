"""Local filesystem storage for uploaded documents."""

from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings


class LocalStorage:
    """Store files under a server-owned directory using generated keys."""

    def __init__(self, root: str) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self._root / key

    def save(self, key: str, data: bytes) -> None:
        self._path(key).write_bytes(data)

    def read(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)


@lru_cache
def get_storage() -> LocalStorage:
    return LocalStorage(get_settings().storage_path)
