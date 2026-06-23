"""
PRISM Repository Model.
"""

from typing import Optional
from sqlalchemy import BigInteger, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from prism.db.base import Base, TimestampMixin, UUIDMixin


class Repository(Base, UUIDMixin, TimestampMixin):
    """GitHub repository connected to a PRISM organization."""
    __tablename__ = "repositories"

    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(512), index=True)
    default_branch: Mapped[str] = mapped_column(String(255), default="main")
    language: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
