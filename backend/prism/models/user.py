"""
PRISM User Model.
"""

from typing import Optional
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from prism.db.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    """User representation mapping to GitHub OAuth accounts."""
    __tablename__ = "users"

    github_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    github_username: Mapped[str] = mapped_column(String(255))
    email: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024))
