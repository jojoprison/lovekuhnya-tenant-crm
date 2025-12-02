from pydantic import BaseModel
from datetime import datetime


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime


class TaskCreate(TaskBase):
    deal_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    is_done: bool | None = None


class TaskResponse(TaskBase):
    id: int
    deal_id: int
    is_done: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
