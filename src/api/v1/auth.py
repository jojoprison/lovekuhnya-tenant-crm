from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.exceptions import ConflictError, UnauthorizedError
from src.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RegisterResponse,
    TokenResponse,
    UserCreate,
)
from src.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register new user with their first organization."""
    try:
        auth_service = AuthService(db)
        result = await auth_service.register(
            email=data.email,
            password=data.password,
            name=data.name,
            organization_name=data.organization_name,
        )
        return RegisterResponse(
            user=result["user"],
            organization_id=result["organization"].id,
            organization_name=result["organization"].name,
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )
    except ConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=e.message
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and get tokens."""
    try:
        auth_service = AuthService(db)
        result = await auth_service.login(
            email=data.email, password=data.password
        )
        return LoginResponse(
            user=result["user"],
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using refresh token."""
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh(data.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )
    except UnauthorizedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=e.message
        )
