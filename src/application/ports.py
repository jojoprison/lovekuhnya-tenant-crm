"""Repository interfaces (ports)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, Sequence

from src.domain.enums import DealStatus, DealStage

if TYPE_CHECKING:
    from src.models import Deal, Task


class DealRepositoryProtocol(Protocol):
    """Port for deal persistence used by DealService."""

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
        ...

    async def count_by_organization(
        self,
        organization_id: int,
        status: list[DealStatus] | None = None,
        stage: DealStage | None = None,
        owner_id: int | None = None,
    ) -> int:
        ...

    async def get_by_id(self, deal_id: int) -> Deal | None:
        ...

    async def create(self, **kwargs) -> Deal:
        ...

    async def update(self, deal: Deal, **kwargs) -> Deal:
        ...

    async def delete(self, deal: Deal) -> None:
        ...


class TaskRepositoryProtocol(Protocol):
    """Port for task persistence used by TaskService."""

    async def get_by_deal(
        self,
        deal_id: int,
        only_open: bool = False,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
    ) -> Sequence[Task]:
        ...

    async def get_by_organization(
        self,
        organization_id: int,
        only_open: bool = False,
        due_before: datetime | None = None,
        due_after: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Task]:
        ...

    async def get_by_id(self, task_id: int) -> Task | None:
        ...

    async def create(self, **kwargs) -> Task:
        ...

    async def update(self, task: Task, **kwargs) -> Task:
        ...

    async def delete(self, task: Task) -> None:
        ...
