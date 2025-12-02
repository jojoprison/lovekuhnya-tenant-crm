from fastapi import APIRouter

from src.api.deps import CurrentUser, DbSession
from src.schemas import OrganizationResponse
from src.services import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/me", response_model=list[OrganizationResponse])
async def get_my_organizations(
    current_user: CurrentUser,
    db: DbSession,
):
    """Get list of organizations where current user is a member."""
    org_service = OrganizationService(db)
    organizations = await org_service.get_user_organizations(current_user)
    return organizations
