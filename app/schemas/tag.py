from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """
    Base schema for tag data.
    """
    name: str = Field(..., min_length=1, max_length=50,
                      description="Name of the tag.")


class TagCreate(TagBase):
    """
    Schema for creating a new tag.
    """
    pass


class TagUpdate(TagBase):
    """
    Schema for updating an existing tag. All fields are optional.
    """
    name: Optional[str] = Field(
        None, min_length=1, max_length=50, description="New name of the tag.")


class TagInDB(TagBase):
    """
    Schema for tag data as stored in the database, including auto-generated fields.
    Used for responses.
    """
    id: int = Field(..., description="Unique identifier for the tag.")
    is_deleted: bool = Field(...,
                             description="Indicates if the tag is soft-deleted.")
    created_at: datetime = Field(...,
                                 description="Timestamp when the tag was created.")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the tag was last updated.")

    model_config = {
        "from_attributes": True
    }
