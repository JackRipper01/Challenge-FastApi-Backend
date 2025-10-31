from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """
    Base schema for user data.
    """
    email: EmailStr = Field(..., description="User's email address.", examples=[
                            "user@example.com"])
    is_active: bool = Field(
        True, description="Indicates if the user account is active.")
    is_superuser: bool = Field(
        False, description="Indicates if the user has superuser privileges.")


class UserCreate(UserBase):
    """
    Schema for creating a new user. Includes password for registration.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=256,
        description="User's password. Must be at least 8 characters long."
    )


class UserUpdate(UserBase):
    """
    Schema for updating an existing user. All fields are optional.
    """
    email: Optional[EmailStr] = Field(
        None, description="New email address for the user.")
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=256,
        description="New password for the user. Must be at least 8 characters long."
    )
    is_active: Optional[bool] = Field(
        None, description="New active status for the user.")
    is_superuser: Optional[bool] = Field(
        None, description="New superuser status for the user.")


class UserInDB(UserBase):
    """
    Schema for user data as stored in the database, including auto-generated fields.
    Used for responses.
    """
    id: int = Field(..., description="Unique identifier for the user.")
    is_deleted: bool = Field(...,
                             description="Indicates if the user is soft-deleted.")
    created_at: datetime = Field(...,
                                 description="Timestamp when the user was created.")
    updated_at: datetime = Field(...,
                                 description="Timestamp when the user was last updated.")

    model_config = {
        "from_attributes": True  # Allow Pydantic to read ORM model attributes
    }
