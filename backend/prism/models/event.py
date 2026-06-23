"""
PRISM Event Log Model.
"""

from typing import Optional
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from prism.db.base import Base, TimestampMixin, UUIDMixin


class Event(Base, UUIDMixin, TimestampMixin):
    """Immutable event log for webhook processing and analysis triggers."""
    __tablename__ = "events"

    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    repo_id: Mapped[Optional[str]] = mapped_column(ForeignKey("repositories.id", ondelete="SET NULL"))
    pr_id: Mapped[Optional[str]] = mapped_column(ForeignKey("pull_requests.id", ondelete="SET NULL"))
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
