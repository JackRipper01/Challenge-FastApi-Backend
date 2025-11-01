from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.base import TimestampMixin, SoftDeleteMixin 


class User(Base, TimestampMixin, SoftDeleteMixin):
    """
    Represents a user in the system.
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    is_active: bool = Column(Boolean, default=True)
    is_superuser: bool = Column(Boolean, default=False)

    # One-to-many relationship: User has many Posts
    posts = relationship("Post", back_populates="owner",
                         cascade="all, delete-orphan")
    # One-to-many relationship: User has many Comments
    comments = relationship(
        "Comment", back_populates="owner", cascade="all, delete-orphan")
