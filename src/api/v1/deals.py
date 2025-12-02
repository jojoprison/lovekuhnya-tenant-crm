from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession, OrgId
from src.core.exceptions import ForbiddenError, NotFoundError, ValidationError
from src.models.enums import DealStage, DealStatus
from src.schemas import DealCreate, DealListResponse, DealResponse, DealUpdate
from src.services import DealService

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.get("", response_model=DealListResponse)
async def get_deals(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: list[DealStatus] | None = Query(None),
    stage: DealStage | None = None,
    owner_id: int | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    order_by: str = Query("created_at", pattern="^(created_at|amount|updated_at)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    """Get paginated list of deals with filters."""
    service = DealService(db)
    deals, total = await service.get_deals(
        organization_id=organization_id,
        user=current_user,
        page=page,
        page_size=page_size,
        status=status,
        stage=stage,
        owner_id=owner_id,
        min_amount=min_amount,
        max_amount=max_amount,
        order_by=order_by,
        order=order,
    )
    return DealListResponse(
        items=deals,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{deal_id}", response_model=DealResponse)
async def get_deal(
    deal_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Get deal by ID."""
    try:
        service = DealService(db)
        return await service.get_deal(deal_id, organization_id, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("", response_model=DealResponse, status_code=status.HTTP_201_CREATED)
async def create_deal(
    data: DealCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Create new deal."""
    try:
        service = DealService(db)
        return await service.create_deal(
            organization_id=organization_id,
            user=current_user,
            contact_id=data.contact_id,
            title=data.title,
            amount=data.amount,
            currency=data.currency,
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.patch("/{deal_id}", response_model=DealResponse)
async def update_deal(
    deal_id: int,
    data: DealUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Update deal (with status/stage validations)."""
    try:
        service = DealService(db)
        return await service.update_deal(
            deal_id=deal_id,
            organization_id=organization_id,
            user=current_user,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Delete deal."""
    try:
        service = DealService(db)
        await service.delete_deal(deal_id, organization_id, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
