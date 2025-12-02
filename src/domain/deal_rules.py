"""Domain rules for deals.

Contains validation logic for deal status and stage transitions.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Sequence

from src.core.exceptions import ValidationError, ForbiddenError
from src.domain.enums import DealStatus, DealStage, UserRole

if TYPE_CHECKING:
    from src.models import Deal, OrganizationMember


STAGE_ORDER: Sequence[DealStage] = [
    DealStage.QUALIFICATION,
    DealStage.PROPOSAL,
    DealStage.NEGOTIATION,
    DealStage.CLOSED,
]


def ensure_status_change_is_valid(
    deal: Deal,
    new_status: DealStatus,
    new_amount: Decimal | None = None,
) -> None:
    """Validate status change rules for a deal.

    Business rule: cannot close a deal as WON if amount <= 0.
    """

    if new_status == DealStatus.WON:
        amount = new_amount if new_amount is not None else deal.amount
        if amount <= 0:
            raise ValidationError("Cannot mark deal as won with amount <= 0")


def ensure_stage_change_is_valid(
    deal: Deal,
    new_stage: DealStage,
    member: OrganizationMember,
) -> None:
    """Validate stage transition rules for a deal.

    Business rule: rollback is only allowed for OWNER / ADMIN roles.
    """

    old_idx = STAGE_ORDER.index(deal.stage)
    new_idx = STAGE_ORDER.index(new_stage)

    if new_idx < old_idx and member.role not in [UserRole.OWNER, UserRole.ADMIN]:
        raise ForbiddenError("Only admin/owner can rollback deal stage")
