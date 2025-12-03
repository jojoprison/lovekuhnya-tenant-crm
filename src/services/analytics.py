from sqlalchemy.ext.asyncio import AsyncSession

from src.core import cache
from src.models import User
from src.repositories import DealRepository
from src.services.organization import OrganizationService

CACHE_TTL = 60  # seconds


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.deal_repo = DealRepository(session)
        self.org_service = OrganizationService(session)

    async def get_deals_summary(
        self,
        organization_id: int,
        user: User,
        days: int = 30,
    ) -> dict:
        """Get deals summary analytics with caching."""
        await self.org_service.get_membership(organization_id, user)

        cache_key = f"analytics:summary:{organization_id}:{days}"
        if cached := cache.get(cache_key):
            return cached

        summary = await self.deal_repo.get_summary(organization_id, days=days)

        result = {
            "by_status": {
                status.value if hasattr(status, "value") else status: {
                    "count": data["count"],
                    "total_amount": float(data["total_amount"]),
                }
                for status, data in summary["by_status"].items()
            },
            "avg_won_amount": float(summary["avg_won_amount"]),
            "new_deals_last_n_days": summary["new_deals_last_n_days"],
            "days": summary["days"],
        }

        cache.set(cache_key, result, CACHE_TTL)
        return result

    async def get_deals_funnel(
        self,
        organization_id: int,
        user: User,
    ) -> dict:
        """Get sales funnel analytics with caching."""
        await self.org_service.get_membership(organization_id, user)

        cache_key = f"analytics:funnel:{organization_id}"
        if cached := cache.get(cache_key):
            return cached

        funnel_data = await self.deal_repo.get_funnel(organization_id)

        result = {
            "stages": {
                stage.value if hasattr(stage, "value") else stage: {
                    "total": data.get("total", 0),
                    "by_status": {
                        s.value if hasattr(s, "value") else s: c
                        for s, c in data.get("by_status", {}).items()
                    },
                    "conversion_from_prev": data.get("conversion_from_prev", 0),
                }
                for stage, data in funnel_data.items()
            }
        }

        cache.set(cache_key, result, CACHE_TTL)
        return result
