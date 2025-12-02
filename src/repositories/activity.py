from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Activity, ActivityType
from src.repositories.base import BaseRepository


class ActivityRepository(BaseRepository[Activity]):
    def __init__(self, session: AsyncSession):
        super().__init__(Activity, session)

    async def get_by_deal(
        self,
        deal_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Activity]:
        """Get activities for a deal, ordered by creation time (newest first)."""
        stmt = (
            select(Activity)
            .where(Activity.deal_id == deal_id)
            .order_by(Activity.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_status_changed(
        self,
        deal_id: int,
        author_id: int | None,
        old_status: str,
        new_status: str,
    ) -> Activity:
        """Create activity for status change."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.STATUS_CHANGED,
            payload={"old_status": old_status, "new_status": new_status},
        )

    async def create_stage_changed(
        self,
        deal_id: int,
        author_id: int | None,
        old_stage: str,
        new_stage: str,
    ) -> Activity:
        """Create activity for stage change."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.STAGE_CHANGED,
            payload={"old_stage": old_stage, "new_stage": new_stage},
        )

    async def create_comment(
        self,
        deal_id: int,
        author_id: int,
        text: str,
    ) -> Activity:
        """Create comment activity."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.COMMENT,
            payload={"text": text},
        )

    async def create_task_created(
        self,
        deal_id: int,
        author_id: int,
        task_id: int,
        task_title: str,
    ) -> Activity:
        """Create activity for task creation."""
        return await self.create(
            deal_id=deal_id,
            author_id=author_id,
            type=ActivityType.TASK_CREATED,
            payload={"task_id": task_id, "task_title": task_title},
        )
