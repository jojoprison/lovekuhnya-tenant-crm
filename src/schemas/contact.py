from datetime import datetime

from pydantic import BaseModel, EmailStr


class ContactBase(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ContactResponse(ContactBase):
    id: int
    organization_id: int
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactListResponse(BaseModel):
    items: list[ContactResponse]
    total: int
    page: int
    page_size: int
