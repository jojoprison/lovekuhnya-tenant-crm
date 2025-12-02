"""Domain layer."""

from src.domain.deal_rules import (
    STAGE_ORDER,
    ensure_stage_change_is_valid,
    ensure_status_change_is_valid,
)
from src.domain.enums import ActivityType, DealStage, DealStatus, UserRole
from src.domain.organization_rules import (
    can_manage_all,
    can_modify_settings,
)
from src.domain.task_rules import ensure_due_date_not_in_past

__all__ = [
    "UserRole",
    "DealStatus",
    "DealStage",
    "ActivityType",
    "STAGE_ORDER",
    "ensure_status_change_is_valid",
    "ensure_stage_change_is_valid",
    "ensure_due_date_not_in_past",
    "can_manage_all",
    "can_modify_settings",
]
