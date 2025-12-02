from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.domain import UserRole, can_manage_all, can_modify_settings
from src.models import Organization, OrganizationMember, User
from src.repositories import OrganizationRepository


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = OrganizationRepository(session)

    async def get_user_organizations(
        self, user: User
    ) -> Sequence[Organization]:
        """Get all organizations where user is a member."""
        return await self.repo.get_user_organizations(user.id)

    async def get_membership(
        self, organization_id: int, user: User
    ) -> OrganizationMember:
        """Get user's membership in organization or raise error."""
        member = await self.repo.get_member(organization_id, user.id)
        if not member:
            raise ForbiddenError("You are not a member of this organization")
        return member

    async def check_permission(
        self,
        organization_id: int,
        user: User,
        required_roles: list[UserRole] | None = None,
    ) -> OrganizationMember:
        """Check if user has required role in organization."""
        member = await self.get_membership(organization_id, user)

        if required_roles and member.role not in required_roles:
            raise ForbiddenError("You don't have permission for this action")

        return member

    async def add_member(
        self,
        organization_id: int,
        user_id: int,
        role: UserRole,
        current_user: User,
    ) -> OrganizationMember:
        """Add new member to organization (admin/owner only)."""
        await self.check_permission(
            organization_id, current_user, [UserRole.OWNER, UserRole.ADMIN]
        )

        # Check if already a member
        existing = await self.repo.get_member(organization_id, user_id)
        if existing:
            raise ValidationError(
                "User is already a member of this organization"
            )

        member = await self.repo.add_member(organization_id, user_id, role)
        await self.session.commit()
        return member

    async def update_member_role(
        self,
        organization_id: int,
        user_id: int,
        new_role: UserRole,
        current_user: User,
    ) -> OrganizationMember:
        """Update member's role (admin/owner only)."""
        await self.check_permission(
            organization_id, current_user, [UserRole.OWNER, UserRole.ADMIN]
        )

        member = await self.repo.get_member(organization_id, user_id)
        if not member:
            raise NotFoundError("Member not found")

        # Only owner can change to/from owner role
        if member.role == UserRole.OWNER or new_role == UserRole.OWNER:
            current_member = await self.repo.get_member(
                organization_id, current_user.id
            )
            if not current_member or current_member.role != UserRole.OWNER:
                raise ForbiddenError("Only owner can change owner role")

        member = await self.repo.update_member_role(member, new_role)
        await self.session.commit()
        return member

    async def remove_member(
        self,
        organization_id: int,
        user_id: int,
        current_user: User,
    ) -> None:
        """Remove member from organization (admin/owner only)."""
        await self.check_permission(
            organization_id, current_user, [UserRole.OWNER, UserRole.ADMIN]
        )

        member = await self.repo.get_member(organization_id, user_id)
        if not member:
            raise NotFoundError("Member not found")

        # Cannot remove owner
        if member.role == UserRole.OWNER:
            raise ValidationError("Cannot remove organization owner")

        await self.repo.remove_member(member)
        await self.session.commit()

    def can_manage_all(self, member: OrganizationMember) -> bool:
        """Check if member can manage all entities (not just their own)."""
        return can_manage_all(member)

    def can_modify_settings(self, member: OrganizationMember) -> bool:
        """Check if member can modify organization settings."""
        return can_modify_settings(member)
