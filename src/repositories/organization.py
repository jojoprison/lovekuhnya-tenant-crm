from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models import Organization, OrganizationMember, UserRole
from src.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, session: AsyncSession):
        super().__init__(Organization, session)

    async def get_user_organizations(self, user_id: int) -> Sequence[Organization]:
        """Get all organizations where user is a member."""
        stmt = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_member(
        self, organization_id: int, user_id: int
    ) -> OrganizationMember | None:
        """Get membership record for user in organization."""
        stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_member(
        self,
        organization_id: int,
        user_id: int,
        role: UserRole = UserRole.MEMBER,
    ) -> OrganizationMember:
        """Add user to organization with specified role."""
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def update_member_role(
        self, member: OrganizationMember, role: UserRole
    ) -> OrganizationMember:
        """Update member's role in organization."""
        member.role = role
        await self.session.flush()
        await self.session.refresh(member)
        return member

    async def remove_member(self, member: OrganizationMember) -> None:
        """Remove user from organization."""
        await self.session.delete(member)
        await self.session.flush()
