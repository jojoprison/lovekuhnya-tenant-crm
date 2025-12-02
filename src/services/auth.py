from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    ConflictError,
    UnauthorizedError,
)
from src.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from src.models import User, UserRole
from src.repositories import OrganizationRepository, UserRepository


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)
        self.org_repo = OrganizationRepository(session)

    async def register(
        self,
        email: str,
        password: str,
        name: str,
        organization_name: str,
    ) -> dict:
        """Register new user with their first organization."""
        # Check if email already exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ConflictError("User with this email already exists")

        # Create user
        hashed = hash_password(password)
        user = await self.user_repo.create(
            email=email,
            hashed_password=hashed,
            name=name,
        )

        # Create organization
        org = await self.org_repo.create(name=organization_name)

        # Add user as owner
        await self.org_repo.add_member(org.id, user.id, UserRole.OWNER)

        await self.session.commit()

        # Generate tokens
        tokens = self._generate_tokens(user.id)

        return {
            "user": user,
            "organization": org,
            **tokens,
        }

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user and return tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")

        tokens = self._generate_tokens(user.id)

        return {
            "user": user,
            **tokens,
        }

    async def refresh(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid refresh token")

        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            raise UnauthorizedError("User not found")

        tokens = self._generate_tokens(user.id)

        return {
            "user": user,
            **tokens,
        }

    async def get_current_user(self, token: str) -> User:
        """Get current user from access token."""
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            raise UnauthorizedError("Invalid access token")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid access token")

        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            raise UnauthorizedError("User not found")

        return user

    def _generate_tokens(self, user_id: int) -> dict:
        return {
            "access_token": create_access_token({"sub": str(user_id)}),
            "refresh_token": create_refresh_token({"sub": str(user_id)}),
            "token_type": "bearer",
        }
