"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.core.security import create_access_token, verify_token
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    PasswordChangeRequest,
    PasswordResetRequest
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    User login endpoint
    
    Authenticates user with email and password, returns JWT tokens
    """
    result = await AuthService.login(db, credentials.email, credentials.password)
    return result


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh JWT access token using refresh token
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    role = payload.get("role")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Generate new access token
    access_token = create_access_token(data={"sub": user_id, "role": role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password
    """
    await AuthService.change_password(
        db,
        current_user,
        request.current_password,
        request.new_password
    )
    
    return {"message": "Password changed successfully"}


@router.post("/reset-password")
async def reset_password(
    request: PasswordResetRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset user password (admin only)
    """
    await AuthService.reset_password(
        db,
        current_user,
        request.email,
        request.new_password
    )
    
    return {"message": "Password reset successfully"}


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "showroom_id": current_user.showroom_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    User logout endpoint
    
    Note: With JWT, logout is handled client-side by removing the token.
    This endpoint can be used for logging purposes.
    """
    return {"message": "Logged out successfully"}
