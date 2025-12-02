from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task
from src.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession):
        super().__init__(Task, session)

    async def get_by_deal(
        self,
        deal_id: int,
        only_open: bool = False,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
    ) -> Sequence[Task]:
        """Get tasks for a deal with optional filters."""
        stmt = select(Task).where(Task.deal_id == deal_id)

        if only_open:
            stmt = stmt.where(Task.is_done == False)

        if due_before:
            stmt = stmt.where(Task.due_date <= due_before)

        if due_after:
            stmt = stmt.where(Task.due_date >= due_after)

        stmt = stmt.order_by(Task.due_date.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_organization(
        self,
        organization_id: int,
        only_open: bool = False,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        """Get all tasks for organization (via deals)."""
        from src.models import Deal

        stmt = select(Task).join(Deal).where(Deal.organization_id == organization_id)

        if only_open:
            stmt = stmt.where(Task.is_done == False)

        if due_before:
            stmt = stmt.where(Task.due_date <= due_before)

        if due_after:
            stmt = stmt.where(Task.due_date >= due_after)

        stmt = stmt.order_by(Task.due_date.asc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_deal(self, deal_id: int, only_open: bool = False) -> int:
        """Count tasks for a deal."""
        stmt = select(func.count()).select_from(Task).where(Task.deal_id == deal_id)

        if only_open:
            stmt = stmt.where(Task.is_done == False)

        result = await self.session.execute(stmt)
        return result.scalar() or 0
