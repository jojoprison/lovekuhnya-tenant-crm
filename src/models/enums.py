"""Backwards-compatible re-export of domain enums.

The canonical enum definitions live in src.domain.enums.
"""

from src.domain.enums import UserRole, DealStatus, DealStage, ActivityType

__all__ = [
    "UserRole",
    "DealStatus",
    "DealStage",
    "ActivityType",
]
