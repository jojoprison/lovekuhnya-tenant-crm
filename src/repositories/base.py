from typing import Generic, TypeVar, Type, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic async repository for CRUD operations."""

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.flush()
