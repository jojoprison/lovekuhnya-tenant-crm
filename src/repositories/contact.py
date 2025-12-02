from typing import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Contact
from src.repositories.base import BaseRepository


class ContactRepository(BaseRepository[Contact]):
    def __init__(self, session: AsyncSession):
        super().__init__(Contact, session)

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> Sequence[Contact]:
        """Get contacts for organization with optional filters."""
        stmt = select(Contact).where(Contact.organization_id == organization_id)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Contact.name.ilike(search_pattern),
                    Contact.email.ilike(search_pattern),
                )
            )

        if owner_id is not None:
            stmt = stmt.where(Contact.owner_id == owner_id)

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_organization(
        self,
        organization_id: int,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> int:
        """Count contacts for organization with optional filters."""
        stmt = (
            select(func.count())
            .select_from(Contact)
            .where(Contact.organization_id == organization_id)
        )

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Contact.name.ilike(search_pattern),
                    Contact.email.ilike(search_pattern),
                )
            )

        if owner_id is not None:
            stmt = stmt.where(Contact.owner_id == owner_id)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def has_deals(self, contact_id: int) -> bool:
        """Check if contact has any deals (for deletion validation)."""
        from src.models import Deal

        stmt = (
            select(func.count()).select_from(Deal).where(Deal.contact_id == contact_id)
        )
        result = await self.session.execute(stmt)
        return (result.scalar() or 0) > 0
