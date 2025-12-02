from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession, OrgId
from src.core.exceptions import NotFoundError, ValidationError
from src.models.enums import ActivityType
from src.schemas import (
    ActivityListResponse,
    ActivityResponse,
    CreateCommentRequest,
)
from src.services import ActivityService

router = APIRouter(prefix="/deals/{deal_id}/activities", tags=["Activities"])


@router.get("", response_model=ActivityListResponse)
async def get_activities(
    deal_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """Get activities (timeline) for a deal."""
    try:
        service = ActivityService(db)
        activities = await service.get_activities(
            deal_id=deal_id,
            organization_id=organization_id,
            user=current_user,
            page=page,
            page_size=page_size,
        )
        return ActivityListResponse(items=activities)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    deal_id: int,
    data: CreateCommentRequest,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Create comment activity (only type users can create directly)."""
    if data.type != ActivityType.COMMENT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only comment activities can be created directly",
        )

    text = data.payload.get("text", "")
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Comment text is required"
        )

    try:
        service = ActivityService(db)
        return await service.create_comment(
            deal_id=deal_id,
            organization_id=organization_id,
            user=current_user,
            text=text,
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
