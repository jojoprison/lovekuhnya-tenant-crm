import asyncio
import logging
from decimal import Decimal

from src.core.database import AsyncSessionLocal
from src.models.enums import DealStage
from src.services import AuthService, ContactService, DealService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def seed_data():
    """Seed database with initial data."""
    async with AsyncSessionLocal() as session:
        auth_service = AuthService(session)
        contact_service = ContactService(session)
        deal_service = DealService(session)

        logger.info("Creating owner user...")
        try:
            # 1. Register Owner
            result = await auth_service.register(
                email="admin@example.com",
                password="admin",  # Simple password for dev
                name="Admin User",
                organization_name="Demo Corp",
            )
            user = result["user"]
            org = result["organization"]
            logger.info(
                f"Created user: {user.email}, Org: {org.name} (ID: {org.id})"
            )

            # 2. Create Contacts
            logger.info("Creating contacts...")
            c1 = await contact_service.create_contact(
                organization_id=org.id,
                user=user,
                name="Alice Smith",
                email="alice@example.com",
                phone="+123456789",
            )
            c2 = await contact_service.create_contact(
                organization_id=org.id,
                user=user,
                name="Bob Jones",
                email="bob@example.com",
            )

            # 3. Create Deals
            logger.info("Creating deals...")
            await deal_service.create_deal(
                organization_id=org.id,
                user=user,
                contact_id=c1.id,
                title="Big Enterprise Contract",
                amount=Decimal("50000.00"),
                currency="USD",
            )

            d2 = await deal_service.create_deal(
                organization_id=org.id,
                user=user,
                contact_id=c2.id,
                title="Small Consulting Gig",
                amount=Decimal("5000.00"),
            )
            # Advance stage for d2
            await deal_service.update_deal(
                deal_id=d2.id,
                organization_id=org.id,
                user=user,
                stage=DealStage.NEGOTIATION,
            )

            logger.info("Seeding complete! 🚀")
            logger.info("Login with: admin@example.com / admin")
            logger.info(f"Organization ID: {org.id}")

        except Exception as e:
            logger.error(f"Seeding failed (maybe already seeded?): {e}")


if __name__ == "__main__":
    asyncio.run(seed_data())
