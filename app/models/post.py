from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.base import TimestampMixin, SoftDeleteMixin
from app.models.tag import post_tag_association

class Post(Base, TimestampMixin, SoftDeleteMixin):
    """
    Represents a post created by a user.
    """
    __tablename__ = "posts"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(256), index=True, nullable=False)
    content: str = Column(Text, nullable=False)
    owner_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)

    # One-to-many relationship: Post belongs to a User
    owner = relationship("User", back_populates="posts")
    # One-to-many relationship: Post has many Comments
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    # Many-to-many relationship: Post has many Tags
    tags = relationship(
        "Tag", secondary=post_tag_association, back_populates="posts")
