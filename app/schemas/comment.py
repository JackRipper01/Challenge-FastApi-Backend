from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.user import UserInDB  # For nested user data


class CommentBase(BaseModel):
    """
    Base schema for comment data.
    """
    content: str = Field(..., min_length=1,
                         description="Content of the comment.")


class CommentCreate(CommentBase):
    """
    Schema for creating a new comment.
    """
    post_id: int = Field(...,
                         description="ID of the post the comment belongs to.")


class CommentUpdate(CommentBase):
    """
    Schema for updating an existing comment. All fields are optional.
    """
    content: Optional[str] = Field(
        None, min_length=1, description="New content of the comment.")


class CommentInDB(CommentBase):
    """
    Schema for comment data as stored in the database, including auto-generated fields and relationships.
    Used for responses.
    """
    id: int = Field(..., description="Unique identifier for the comment.")
    owner_id: int = Field(...,
                          description="ID of the user who created the comment.")
    post_id: int = Field(...,
                         description="ID of the post the comment belongs to.")
    is_deleted: bool = Field(...,
                             description="Indicates if the comment is soft-deleted.")
    created_at: datetime = Field(...,
                                 description="Timestamp when the comment was created.")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the comment was last updated.")

    owner: Optional[UserInDB] = None  # Nested user data

    model_config = {
        "from_attributes": True
    }
