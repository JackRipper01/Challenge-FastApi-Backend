from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """
    Schema for the JWT token response.
    """
    access_token: str = Field(..., description="The JWT access token.")
    token_type: str = Field(
        "bearer", description="Type of the token, typically 'bearer'.")


class TokenData(BaseModel):
    """
    Schema for data extracted from the JWT token payload.
    """
    id: Optional[int] = Field(
        None, description="User ID from the token payload.")


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """
    email: EmailStr = Field(..., description="User's email for login.")
    password: str = Field(..., description="User's password for login.")
