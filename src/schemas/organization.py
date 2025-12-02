from pydantic import BaseModel
from datetime import datetime
from src.models.enums import UserRole


class OrganizationResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationMemberResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: UserRole

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    user_id: int
    role: UserRole = UserRole.MEMBER


class UpdateMemberRoleRequest(BaseModel):
    role: UserRole
