"""
PRISM Analysis Model.
"""

from sqlalchemy import Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from prism.db.base import Base, TimestampMixin, UUIDMixin


class Analysis(Base, UUIDMixin, TimestampMixin):
    """Stores the risk analysis results for a Pull Request."""
    __tablename__ = "analyses"

    pr_id: Mapped[str] = mapped_column(ForeignKey("pull_requests.id", ondelete="CASCADE"), index=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(50))  # low, medium, high, critical
    categories: Mapped[list[str]] = mapped_column(JSON, default=list)
    findings: Mapped[list[dict]] = mapped_column(JSON, default=list)
