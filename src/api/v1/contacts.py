from fastapi import APIRouter, HTTPException, Query, status

from src.api.deps import CurrentUser, DbSession, OrgId
from src.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from src.schemas import (
    ContactCreate,
    ContactListResponse,
    ContactResponse,
    ContactUpdate,
)
from src.services import ContactService

router = APIRouter(prefix="/contacts", tags=["Contacts"])


@router.get("", response_model=ContactListResponse)
async def get_contacts(
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    owner_id: int | None = None,
):
    """Get paginated list of contacts."""
    service = ContactService(db)
    contacts, total = await service.get_contacts(
        organization_id=organization_id,
        user=current_user,
        page=page,
        page_size=page_size,
        search=search,
        owner_id=owner_id,
    )
    return ContactListResponse(
        items=contacts,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Get contact by ID."""
    try:
        service = ContactService(db)
        return await service.get_contact(contact_id, organization_id, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    data: ContactCreate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Create new contact."""
    service = ContactService(db)
    return await service.create_contact(
        organization_id=organization_id,
        user=current_user,
        name=data.name,
        email=data.email,
        phone=data.phone,
    )


@router.patch("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Update contact."""
    try:
        service = ContactService(db)
        return await service.update_contact(
            contact_id=contact_id,
            organization_id=organization_id,
            user=current_user,
            **data.model_dump(exclude_unset=True),
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    db: DbSession,
    current_user: CurrentUser,
    organization_id: OrgId,
):
    """Delete contact (only if no deals)."""
    try:
        service = ContactService(db)
        await service.delete_contact(contact_id, organization_id, current_user)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except ForbiddenError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
