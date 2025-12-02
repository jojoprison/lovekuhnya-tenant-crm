from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession, OrgId
from src.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.schemas import TaskCreate, TaskListResponse, TaskResponse, TaskUpdate
from src.services import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
    deal_id: int | None = None,
    only_open: bool = False,
    due_before: datetime | None = None,
    due_after: datetime | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get tasks with optional filters."""
    try:
        service = TaskService(db)
        tasks = await service.get_tasks(
            organization_id=organization_id,
            user=current_user,
            deal_id=deal_id,
            only_open=only_open,
            due_before=due_before,
            due_after=due_after,
            page=page,
            page_size=page_size,
        )
        return TaskListResponse(items=tasks)  # type: ignore[arg-type]
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Get task by ID."""
    try:
        service = TaskService(db)
        return await service.get_task(task_id, organization_id, current_user)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )


@router.post(
    "", response_model=TaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_task(
    data: TaskCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Create new task for a deal."""
    try:
        service = TaskService(db)
        return await service.create_task(
            organization_id=organization_id,
            user=current_user,
            deal_id=data.deal_id,
            title=data.title,
            due_date=data.due_date,
            description=data.description,
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=e.message
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
        )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Update task."""
    try:
        service = TaskService(db)
        return await service.update_task(
            task_id=task_id,
            organization_id=organization_id,
            user=current_user,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=e.message
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Delete task."""
    try:
        service = TaskService(db)
        await service.delete_task(task_id, organization_id, current_user)
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=e.message
        )
    except ForbiddenError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=e.message
        )
