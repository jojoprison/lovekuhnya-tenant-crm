from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError, ForbiddenError, ConflictError
from src.repositories import ContactRepository
from src.models import Contact, User, OrganizationMember, UserRole
from src.services.organization import OrganizationService


class ContactService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ContactRepository(session)
        self.org_service = OrganizationService(session)

    async def get_contacts(
        self,
        organization_id: int,
        user: User,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> tuple[Sequence[Contact], int]:
        """Get paginated contacts for organization."""
        member = await self.org_service.get_membership(organization_id, user)

        # Members can only filter by owner if it's themselves
        if owner_id is not None and not self.org_service.can_manage_all(member):
            owner_id = user.id

        skip = (page - 1) * page_size
        contacts = await self.repo.get_by_organization(
            organization_id,
            skip=skip,
            limit=page_size,
            search=search,
            owner_id=owner_id,
        )
        total = await self.repo.count_by_organization(
            organization_id, search=search, owner_id=owner_id
        )

        return contacts, total

    async def get_contact(
        self,
        contact_id: int,
        organization_id: int,
        user: User,
    ) -> Contact:
        """Get single contact by ID."""
        await self.org_service.get_membership(organization_id, user)

        contact = await self.repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise NotFoundError("Contact not found")

        return contact

    async def create_contact(
        self,
        organization_id: int,
        user: User,
        name: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> Contact:
        """Create new contact."""
        await self.org_service.get_membership(organization_id, user)

        contact = await self.repo.create(
            organization_id=organization_id,
            owner_id=user.id,
            name=name,
            email=email,
            phone=phone,
        )
        await self.session.commit()
        return contact

    async def update_contact(
        self,
        contact_id: int,
        organization_id: int,
        user: User,
        **kwargs,
    ) -> Contact:
        """Update contact."""
        member = await self.org_service.get_membership(organization_id, user)

        contact = await self.repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise NotFoundError("Contact not found")

        # Members can only update their own contacts
        if not self.org_service.can_manage_all(member) and contact.owner_id != user.id:
            raise ForbiddenError("You can only update your own contacts")

        # Filter out None values and owner_id (shouldn't be changed)
        update_data = {k: v for k, v in kwargs.items() if v is not None and k != "owner_id"}

        contact = await self.repo.update(contact, **update_data)
        await self.session.commit()
        return contact

    async def delete_contact(
        self,
        contact_id: int,
        organization_id: int,
        user: User,
    ) -> None:
        """Delete contact (only if no deals)."""
        member = await self.org_service.get_membership(organization_id, user)

        contact = await self.repo.get_by_id(contact_id)
        if not contact or contact.organization_id != organization_id:
            raise NotFoundError("Contact not found")

        # Members can only delete their own contacts
        if not self.org_service.can_manage_all(member) and contact.owner_id != user.id:
            raise ForbiddenError("You can only delete your own contacts")

        # Check for existing deals
        if await self.repo.has_deals(contact_id):
            raise ConflictError("Cannot delete contact with existing deals")

        await self.repo.delete(contact)
        await self.session.commit()
