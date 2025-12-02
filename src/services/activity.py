from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError, ValidationError
from src.models import Activity, ActivityType, User
from src.repositories import ActivityRepository, DealRepository
from src.services.organization import OrganizationService


class ActivityService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ActivityRepository(session)
        self.deal_repo = DealRepository(session)
        self.org_service = OrganizationService(session)

    async def get_activities(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
        page: int = 1,
        page_size: int = 50,
    ) -> Sequence[Activity]:
        """Get activities for a deal."""
        await self.org_service.get_membership(organization_id, user)

        # Validate deal belongs to organization
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        skip = (page - 1) * page_size
        return await self.repo.get_by_deal(deal_id, skip=skip, limit=page_size)

    async def create_comment(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
        text: str,
    ) -> Activity:
        """Create comment activity (only type users can create directly)."""
        await self.org_service.get_membership(organization_id, user)

        # Validate deal belongs to organization
        deal = await self.deal_repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        if not text or not text.strip():
            raise ValidationError("Comment text cannot be empty")

        activity = await self.repo.create_comment(
            deal_id=deal_id,
            author_id=user.id,
            text=text.strip(),
        )
        await self.session.commit()
        return activity
