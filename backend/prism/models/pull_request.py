"""
PRISM Pull Request Model.
"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from prism.db.base import Base, TimestampMixin, UUIDMixin


class PullRequest(Base, UUIDMixin, TimestampMixin):
    """GitHub pull request being analyzed by PRISM."""

    __tablename__ = "pull_requests"

    repo_id: Mapped[str] = mapped_column(
        ForeignKey("repositories.id", ondelete="CASCADE"), index=True
    )
    github_pr_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String)
    author: Mapped[str] = mapped_column(String(255), index=True)
    state: Mapped[str] = mapped_column(String(50), index=True)  # open, closed, merged
    base_branch: Mapped[str] = mapped_column(String(255))
    head_branch: Mapped[str] = mapped_column(String(255))
    files_changed: Mapped[int] = mapped_column(Integer, default=0)
    additions: Mapped[int] = mapped_column(Integer, default=0)
    deletions: Mapped[int] = mapped_column(Integer, default=0)
    merged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
