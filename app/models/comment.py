from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.db.base import TimestampMixin, SoftDeleteMixin


class Comment(Base, TimestampMixin, SoftDeleteMixin):
    """
    Represents a comment on a post, made by a user.
    """
    __tablename__ = "comments"

    id: int = Column(Integer, primary_key=True, index=True)
    content: str = Column(Text, nullable=False)
    owner_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id: int = Column(Integer, ForeignKey("posts.id"), nullable=False)

    # One-to-many relationship: Comment belongs to a User
    owner = relationship("User", back_populates="comments")
    # One-to-many relationship: Comment belongs to a Post
    post = relationship("Post", back_populates="comments")
