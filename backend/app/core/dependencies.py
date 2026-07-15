"""
FastAPI dependencies for authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extract token
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # Extract user ID from token
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Fetch user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


# Role-based access control dependencies

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_showroom_manager(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require showroom manager role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SHOWROOM]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Showroom manager access required"
        )
    return current_user


async def require_mechanic(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require mechanic role"""
    if current_user.role not in [UserRole.ADMIN, UserRole.SHOWROOM, UserRole.MECHANIC]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Mechanic access required"
        )
    return current_user


async def require_owner(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require vehicle owner role"""
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vehicle owner access required"
        )
    return current_user


def require_role(*allowed_roles: UserRole):
    """
    Decorator factory for requiring specific roles
    
    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(UserRole.ADMIN))])
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user
    
    return role_checker


def require_showroom_access(showroom_id: int):
    """
    Verify user has access to a specific showroom
    
    - Admins can access any showroom
    - Showroom/Mechanic users can only access their assigned showroom
    """
    async def showroom_checker(current_user: User = Depends(get_current_user)) -> User:
        # Admin can access any showroom
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Showroom/Mechanic users must match showroom_id
        if current_user.role in [UserRole.SHOWROOM, UserRole.MECHANIC]:
            if current_user.showroom_id != showroom_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this showroom"
                )
            return current_user
        
        # Owners don't have showroom-level access
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return showroom_checker


def require_vehicle_access(owner_id: int):
    """
    Verify user has access to a specific vehicle
    
    - Admins can access any vehicle
    - Owners can only access their own vehicles
    - Showroom staff can access vehicles in their showroom
    """
    async def vehicle_checker(current_user: User = Depends(get_current_user)) -> User:
        # Admin can access any vehicle
        if current_user.role == UserRole.ADMIN:
            return current_user
        
        # Owner must match
        if current_user.role == UserRole.OWNER:
            if current_user.id != owner_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this vehicle"
                )
            return current_user
        
        # Showroom/Mechanic access is checked at the query level
        # based on vehicle's home_showroom_id
        if current_user.role in [UserRole.SHOWROOM, UserRole.MECHANIC]:
            return current_user
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    return vehicle_checker
