"""Task validation rules."""

from datetime import UTC, datetime

from src.core.exceptions import ValidationError


def ensure_due_date_not_in_past(due_date: datetime) -> None:
    today = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    if due_date.replace(tzinfo=UTC) < today:
        raise ValidationError("Due date cannot be in the past")
