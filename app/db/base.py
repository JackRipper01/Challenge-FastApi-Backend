from datetime import datetime
from typing import TypeVar, Type

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.orm import declarative_mixin, declared_attr

# Define a type variable for the ORM model instances
_T = TypeVar("_T", bound=Type)


@declarative_mixin
class TimestampMixin:
    """
    Mixin that adds 'created_at' and 'updated_at' fields to SQLAlchemy models.
    'created_at' is set once on creation.
    'updated_at' is automatically updated on every modification.
    """
    @declared_attr
    def created_at(cls):
        """Timestamp for when the record was created."""
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        """Timestamp for when the record was last updated."""
        return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


@declarative_mixin
class SoftDeleteMixin:
    """
    Mixin that adds a 'is_deleted' flag for soft deletion.
    Entities with is_deleted=True should not appear in default query listings.
    """
    @declared_attr
    def is_deleted(cls):
        """Flag indicating if the record is soft-deleted."""
        return Column(Boolean, default=False, nullable=False)

    # Note: A custom query to filter out deleted items is implemented
    # directly in the service layer or router by adding `.filter(Model.is_deleted == False)`.
    # This approach gives more flexibility than attempting to modify default ORM query behavior
    # globally via `__mapper_args__` which can be complex with async sessions and relationships.
