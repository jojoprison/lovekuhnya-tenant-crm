from fastapi import APIRouter, Query

from src.api.deps import DbSession, CurrentUser, OrgId
from src.services import AnalyticsService
from src.schemas import DealsSummaryResponse, DealsFunnelResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/deals/summary", response_model=DealsSummaryResponse)
async def get_deals_summary(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
    days: int = Query(30, ge=1, le=365),
):
    """Get deals summary analytics."""
    service = AnalyticsService(db)
    return await service.get_deals_summary(
        organization_id=organization_id,
        user=current_user,
        days=days,
    )


@router.get("/deals/funnel", response_model=DealsFunnelResponse)
async def get_deals_funnel(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Get sales funnel analytics."""
    service = AnalyticsService(db)
    return await service.get_deals_funnel(
        organization_id=organization_id,
        user=current_user,
    )
