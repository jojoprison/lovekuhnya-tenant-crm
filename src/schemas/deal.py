from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.models.enums import DealStage, DealStatus


class DealBase(BaseModel):
    title: str
    amount: Decimal = Decimal(0)
    currency: str = "USD"


class DealCreate(DealBase):
    contact_id: int


class DealUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    status: DealStatus | None = None
    stage: DealStage | None = None


class DealResponse(DealBase):
    id: int
    organization_id: int
    contact_id: int
    owner_id: int
    status: DealStatus
    stage: DealStage
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DealListResponse(BaseModel):
    items: list[DealResponse]
    total: int
    page: int
    page_size: int
