from collections.abc import Sequence
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports import DealRepositoryProtocol
from src.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.domain import (
    DealStage,
    DealStatus,
    ensure_stage_change_is_valid,
    ensure_status_change_is_valid,
)
from src.models import Deal, User
from src.repositories import (
    ActivityRepository,
    ContactRepository,
    DealRepository,
)
from src.services.organization import OrganizationService


class DealService:
    def __init__(
        self,
        session: AsyncSession,
        deal_repo: DealRepositoryProtocol | None = None,
    ) -> None:
        self.session = session
        self.repo = deal_repo or DealRepository(session)
        self.contact_repo = ContactRepository(session)
        self.activity_repo = ActivityRepository(session)
        self.org_service = OrganizationService(session)

    async def get_deals(
        self,
        organization_id: int,
        user: User,
        page: int = 1,
        page_size: int = 20,
        status: list[DealStatus] | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> tuple[Sequence[Deal], int]:
        """Get paginated deals for organization."""
        member = await self.org_service.get_membership(organization_id, user)

        # Members can only filter by owner if it's themselves
        if owner_id is not None and not self.org_service.can_manage_all(member):
            owner_id = user.id

        skip = (page - 1) * page_size
        deals = await self.repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=page_size,
            status=status,
            stage=stage,
            owner_id=owner_id,
            min_amount=min_amount,
            max_amount=max_amount,
            order_by=order_by,
            order=order,
        )
        total = await self.repo.count_by_organization(
            organization_id, status=status, stage=stage, owner_id=owner_id
        )

        return deals, total

    async def get_deal(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
    ) -> Deal:
        """Get single deal by ID."""
        await self.org_service.get_membership(organization_id, user)

        deal = await self.repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        return deal

    async def create_deal(
        self,
        organization_id: int,
        user: User,
        contact_id: int,
        title: str,
        amount: Decimal = Decimal(0),
        currency: str = "USD",
    ) -> Deal:
        """Create new deal."""
        await self.org_service.get_membership(organization_id, user)

        # Validate contact belongs to same organization
        contact = await self.contact_repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise ValidationError("Contact not found in this organization")

        deal = await self.repo.create(
            organization_id=organization_id,
            contact_id=contact_id,
            owner_id=user.id,
            title=title,
            amount=amount,
            currency=currency,
            status=DealStatus.NEW,
            stage=DealStage.QUALIFICATION,
        )
        await self.session.commit()
        return deal

    async def update_deal(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
        status: DealStatus | None = None,
        stage: DealStage | None = None,
        **kwargs,
    ) -> Deal:
        """Update deal with business rule validations."""
        member = await self.org_service.get_membership(organization_id, user)

        deal = await self.repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        # Members can only update their own deals
        if (
            not self.org_service.can_manage_all(member)
            and deal.owner_id != user.id
        ):
            raise ForbiddenError("You can only update your own deals")

        # Validate status change
        if status is not None:
            ensure_status_change_is_valid(deal, status, kwargs.get("amount"))

        # Validate stage change
        if stage is not None:
            ensure_stage_change_is_valid(deal, stage, member)

        # Build update data
        update_data = {
            k: v
            for k, v in kwargs.items()
            if v is not None
            and k not in ["owner_id", "organization_id", "contact_id"]
        }

        old_status = deal.status
        old_stage = deal.stage

        if status is not None:
            update_data["status"] = status
        if stage is not None:
            update_data["stage"] = stage

        deal = await self.repo.update(deal, **update_data)

        # Create activity records for status/stage changes
        if status is not None and status != old_status:
            await self.activity_repo.create_status_changed(
                deal_id=deal.id,
                author_id=user.id,
                old_status=old_status.value,
                new_status=status.value,
            )

        if stage is not None and stage != old_stage:
            await self.activity_repo.create_stage_changed(
                deal_id=deal.id,
                author_id=user.id,
                old_stage=old_stage.value,
                new_stage=stage.value,
            )

        await self.session.commit()
        return deal

    async def delete_deal(
        self,
        deal_id: int,
        organization_id: int,
        user: User,
    ) -> None:
        """Delete deal."""
        member = await self.org_service.get_membership(organization_id, user)

        deal = await self.repo.get_by_id(deal_id)
        if not deal or deal.organization_id != organization_id:
            raise NotFoundError("Deal not found")

        # Members can only delete their own deals
        if (
            not self.org_service.can_manage_all(member)
            and deal.owner_id != user.id
        ):
            raise ForbiddenError("You can only delete your own deals")

        await self.repo.delete(deal)
        await self.session.commit()
