from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.domain.enums import ActivityType, DealStage, DealStatus


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    name: Mapped[str] = mapped_column(String, index=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="contacts")
    owner: Mapped["User"] = relationship()
    deals: Mapped[List["Deal"]] = relationship(back_populates="contact")


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    contact_id: Mapped[int] = mapped_column(ForeignKey("contacts.id"))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    title: Mapped[str] = mapped_column(String)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    currency: Mapped[str] = mapped_column(String, default="USD")
    status: Mapped[DealStatus] = mapped_column(
        SAEnum(DealStatus), default=DealStatus.NEW
    )
    stage: Mapped[DealStage] = mapped_column(
        SAEnum(DealStage), default=DealStage.QUALIFICATION
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="deals")
    contact: Mapped["Contact"] = relationship(back_populates="deals")
    owner: Mapped["User"] = relationship()
    tasks: Mapped[List["Task"]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )
    activities: Mapped[List["Activity"]] = relationship(
        back_populates="deal", cascade="all, delete-orphan"
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"))

    title: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    deal: Mapped["Deal"] = relationship(back_populates="tasks")


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("deals.id"))
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )

    type: Mapped[ActivityType] = mapped_column(SAEnum(ActivityType))
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    deal: Mapped["Deal"] = relationship(back_populates="activities")
    author: Mapped["User"] = relationship()
