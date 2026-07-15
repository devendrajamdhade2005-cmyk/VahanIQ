"""
User schemas for API validation
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=100)
    showroom_id: Optional[int] = None


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    showroom_id: Optional[int] = None


class UserInDB(UserBase):
    """Schema for user stored in database"""
    id: int
    showroom_id: Optional[int]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """Schema for user API responses"""
    id: int
    showroom_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
