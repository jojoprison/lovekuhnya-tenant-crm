"""Infrastructure layer: DB, configuration, security, persistence.

Currently this layer re-exports pieces from src.core and src.repositories
without changing their internal structure.
"""

from src.core.config import settings
from src.core.database import Base, AsyncSessionLocal, get_db
from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)

import src.repositories as repositories

__all__ = [
    "settings",
    "Base",
    "AsyncSessionLocal",
    "get_db",
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "repositories",
]
