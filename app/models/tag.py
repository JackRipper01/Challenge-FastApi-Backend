from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint  
from sqlalchemy.schema import Index  # Import Index for partial index

from app.db.session import Base
from app.db.base import TimestampMixin, SoftDeleteMixin

# Association table for the many-to-many relationship between Post and Tag
post_tag_association = Table(
    "post_tag_association",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)


class Tag(Base, TimestampMixin, SoftDeleteMixin):
    """
    Represents a tag that can be associated with posts.
    """
    __tablename__ = "tags"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String(50), index=True, nullable=False)

    # Many-to-many relationship: Tag has many Posts
    posts = relationship(
        "Post", secondary=post_tag_association, back_populates="tags")

    # Define a partial unique index for the 'name' column for PostgreSQL
    # This ensures 'name' is unique only for tags where 'is_deleted' is False
    __table_args__ = (
        Index(
            'uq_tag_name_non_deleted',
            'name',
            unique=True,
            postgresql_where=Column('is_deleted') == False
        ),
    )
