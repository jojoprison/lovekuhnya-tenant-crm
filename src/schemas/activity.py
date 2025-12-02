from datetime import datetime
from typing import Any

from pydantic import BaseModel

from src.models.enums import ActivityType


class ActivityResponse(BaseModel):
    id: int
    deal_id: int
    author_id: int | None
    type: ActivityType
    payload: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    items: list[ActivityResponse]


class CreateCommentRequest(BaseModel):
    type: ActivityType = ActivityType.COMMENT
    payload: dict[str, str]  # {"text": "..."}
