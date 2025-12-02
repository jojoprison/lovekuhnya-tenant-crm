"""Domain rules for organization membership and roles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.domain.enums import UserRole

if TYPE_CHECKING:
    from src.models.auth import OrganizationMember


def can_manage_all(member: OrganizationMember) -> bool:
    """Return True if member can manage all entities in an organization."""

    return member.role in (UserRole.OWNER, UserRole.ADMIN, UserRole.MANAGER)


def can_modify_settings(member: OrganizationMember) -> bool:
    """Return True if member can modify organization-level settings."""

    return member.role in (UserRole.OWNER, UserRole.ADMIN)
