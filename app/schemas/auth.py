from pydantic import BaseModel, Field,ConfigDict
from datetime import date
from typing import Optional
from uuid import UUID

from app.models.user import UserRole


# Auth Schemas
class LoginRequest(BaseModel):
    """Login request schema"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: "UserResponse"


class TokenData(BaseModel):
    """Token data schema"""
    user_id: str
    role: UserRole
