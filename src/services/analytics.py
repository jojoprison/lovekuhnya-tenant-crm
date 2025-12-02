from sqlalchemy.ext.asyncio import AsyncSession
from functools import lru_cache
from datetime import datetime, timedelta

from src.repositories import DealRepository
from src.models import User
from src.services.organization import OrganizationService


# Simple in-memory cache for analytics
_cache: dict[str, tuple[datetime, dict]] = {}
CACHE_TTL_SECONDS = 60  # Cache for 60 seconds


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

        cache_key = f"summary_{organization_id}_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        summary = await self.deal_repo.get_summary(organization_id, days=days)

        # Format response
        result = {
            "by_status": {
                status.value if hasattr(status, 'value') else status: {
                    "count": data["count"],
                    "total_amount": float(data["total_amount"]),
                }
                for status, data in summary["by_status"].items()
            },
            "avg_won_amount": float(summary["avg_won_amount"]),
            "new_deals_last_n_days": summary["new_deals_last_n_days"],
            "days": summary["days"],
        }

        self._set_cached(cache_key, result)
        return result

    async def get_deals_funnel(
        self,
        organization_id: int,
        user: User,
    ) -> dict:
        """Get sales funnel analytics with caching."""
        await self.org_service.get_membership(organization_id, user)

        cache_key = f"funnel_{organization_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        funnel_data = await self.deal_repo.get_funnel(organization_id)

        # Format response
        result = {
            "stages": {
                stage.value if hasattr(stage, 'value') else stage: {
                    "total": data.get("total", 0),
                    "by_status": {
                        s.value if hasattr(s, 'value') else s: c
                        for s, c in data.get("by_status", {}).items()
                    },
                    "conversion_from_prev": data.get("conversion_from_prev", 0),
                }
                for stage, data in funnel_data.items()
            }
        }

        self._set_cached(cache_key, result)
        return result

    def _get_cached(self, key: str) -> dict | None:
        """Get value from cache if not expired."""
        if key in _cache:
            cached_at, value = _cache[key]
            if datetime.utcnow() - cached_at < timedelta(seconds=CACHE_TTL_SECONDS):
                return value
            del _cache[key]
        return None

    def _set_cached(self, key: str, value: dict) -> None:
        """Set value in cache."""
        _cache[key] = (datetime.utcnow(), value)

    @staticmethod
    def clear_cache(organization_id: int | None = None) -> None:
        """Clear cache for organization or all."""
        global _cache
        if organization_id:
            keys_to_delete = [k for k in _cache if f"_{organization_id}_" in k or k.endswith(f"_{organization_id}")]
            for k in keys_to_delete:
                del _cache[k]
        else:
            _cache = {}
