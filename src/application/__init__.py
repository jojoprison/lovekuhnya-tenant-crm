"""Application layer: use cases / services.

For now this layer re-exports existing service classes from src.services
so that the dependency direction (interface -> application -> infrastructure)
can be expressed without rewriting business logic.
"""

from src.services import (
    AuthService,
    OrganizationService,
    ContactService,
    DealService,
    TaskService,
    ActivityService,
    AnalyticsService,
)

__all__ = [
    "AuthService",
    "OrganizationService",
    "ContactService",
    "DealService",
    "TaskService",
    "ActivityService",
    "AnalyticsService",
]
