"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class UserInfo(BaseModel):
    """User information in login response"""
    id: int
    email: str
    full_name: str
    role: str
    showroom_id: Optional[int] = None
    is_active: bool
    created_at: datetime


class LoginResponse(BaseModel):
    """Login response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserInfo


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Refresh token response"""
    access_token: str
    token_type: str = "bearer"


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    """Password reset request (for admin)"""
    email: EmailStr
    new_password: str = Field(..., min_length=8, max_length=100)


class TokenPayload(BaseModel):
    """Token payload schema"""
    sub: int  # User ID
    role: str
    exp: int
