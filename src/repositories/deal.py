from datetime import datetime, timedelta
from decimal import Decimal
from typing import Sequence

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Deal, DealStage, DealStatus
from src.repositories.base import BaseRepository


class DealRepository(BaseRepository[Deal]):
    def __init__(self, session: AsyncSession):
        super().__init__(Deal, session)

    async def get_by_organization(
        self,
        organization_id: int,
        skip: int = 0,
        limit: int = 100,
        status: list[DealStatus] | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> Sequence[Deal]:
        """Get deals for organization with filters and sorting."""
        stmt = select(Deal).where(Deal.organization_id == organization_id)

        if status:
            stmt = stmt.where(Deal.status.in_(status))

        if stage:
            stmt = stmt.where(Deal.stage == stage)

        if owner_id is not None:
            stmt = stmt.where(Deal.owner_id == owner_id)

        if min_amount is not None:
            stmt = stmt.where(Deal.amount >= min_amount)

        if max_amount is not None:
            stmt = stmt.where(Deal.amount <= max_amount)

        # Sorting
        order_column = getattr(Deal, order_by, Deal.created_at)
        if order == "asc":
            stmt = stmt.order_by(order_column.asc())
        else:
            stmt = stmt.order_by(order_column.desc())

        stmt = stmt.offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_organization(
        self,
        organization_id: int,
        status: list[DealStatus] | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
    ) -> int:
        """Count deals for organization with optional filters."""
        stmt = (
            select(func.count())
            .select_from(Deal)
            .where(Deal.organization_id == organization_id)
        )

        if status:
            stmt = stmt.where(Deal.status.in_(status))

        if stage:
            stmt = stmt.where(Deal.stage == stage)

        if owner_id is not None:
            stmt = stmt.where(Deal.owner_id == owner_id)

        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_summary(self, organization_id: int, days: int = 30) -> dict:
        """Get deals summary for analytics."""
        # Count and sum by status
        stmt = (
            select(
                Deal.status,
                func.count(Deal.id).label("count"),
                func.sum(Deal.amount).label("total_amount"),
            )
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.status)
        )
        result = await self.session.execute(stmt)
        by_status = {
            row.status: {
                "count": row.count,
                "total_amount": row.total_amount or Decimal(0),
            }
            for row in result
        }

        # Average amount for won deals
        stmt_avg = select(func.avg(Deal.amount)).where(
            Deal.organization_id == organization_id,
            Deal.status == DealStatus.WON,
        )
        avg_result = await self.session.execute(stmt_avg)
        avg_won = avg_result.scalar() or Decimal(0)

        # New deals in last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt_new = (
            select(func.count())
            .select_from(Deal)
            .where(
                Deal.organization_id == organization_id,
                Deal.created_at >= cutoff_date,
            )
        )
        new_result = await self.session.execute(stmt_new)
        new_count = new_result.scalar() or 0

        return {
            "by_status": by_status,
            "avg_won_amount": avg_won,
            "new_deals_last_n_days": new_count,
            "days": days,
        }

    async def get_funnel(self, organization_id: int) -> dict:
        """Get sales funnel data for analytics."""
        stmt = (
            select(
                Deal.stage,
                Deal.status,
                func.count(Deal.id).label("count"),
            )
            .where(Deal.organization_id == organization_id)
            .group_by(Deal.stage, Deal.status)
        )
        result = await self.session.execute(stmt)

        funnel = {}
        for row in result:
            stage = row.stage
            if stage not in funnel:
                funnel[stage] = {"total": 0, "by_status": {}}
            funnel[stage]["total"] += row.count
            funnel[stage]["by_status"][row.status] = row.count

        # Calculate conversion rates
        stages = list(DealStage)
        for i, stage in enumerate(stages[1:], 1):
            prev_stage = stages[i - 1]
            prev_total = funnel.get(prev_stage, {}).get("total", 0)
            curr_total = funnel.get(stage, {}).get("total", 0)
            if prev_total > 0:
                funnel.setdefault(stage, {})["conversion_from_prev"] = round(
                    curr_total / prev_total * 100, 2
                )
            else:
                funnel.setdefault(stage, {})["conversion_from_prev"] = 0

        return funnel
