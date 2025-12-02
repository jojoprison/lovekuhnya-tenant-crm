"""Domain rules for tasks."""

from datetime import datetime

from src.core.exceptions import ValidationError


def ensure_due_date_not_in_past(due_date: datetime) -> None:
    """Validate that due_date is not in the past (min: today UTC)."""

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    if due_date < today:
        raise ValidationError("Due date cannot be in the past")
