from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.schemas.user import UserInDB
from app.schemas.comment import CommentInDB


class PostBase(BaseModel):
    """
    Base schema for post data.
    """
    title: str = Field(..., min_length=1, max_length=256,
                       description="Title of the post.")
    content: str = Field(..., min_length=1, description="Content of the post.")


class PostCreate(PostBase):
    """
    Schema for creating a new post.
    """
    pass


class PostUpdate(PostBase):
    """
    Schema for updating an existing post. All fields are optional.
    """
    title: Optional[str] = Field(
        None, min_length=1, max_length=256, description="New title of the post.")
    content: Optional[str] = Field(
        None, min_length=1, description="New content of the post.")


class PostInDB(PostBase):
    """
    Schema for post data as stored in the database, including auto-generated fields and relationships.
    Used for responses.
    """
    id: int = Field(..., description="Unique identifier for the post.")
    owner_id: int = Field(...,
                          description="ID of the user who created the post.")
    is_deleted: bool = Field(...,
                             description="Indicates if the post is soft-deleted.")
    created_at: datetime = Field(...,
                                 description="Timestamp when the post was created.")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the post was last updated.")

    owner: Optional[UserInDB] = None
    comments: List[CommentInDB] = []

    model_config = {
        "from_attributes": True
    }


# This line is good practice for Pydantic to resolve forward references correctly
# when models reference each other (Circular Dependency xd).
PostInDB.model_rebuild()
