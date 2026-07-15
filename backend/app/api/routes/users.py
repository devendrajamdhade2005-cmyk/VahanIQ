"""
User management routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin, require_showroom_manager
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.audit import AuditLog
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    role: UserRole = Query(None, description="Filter by role"),
    showroom_id: int = Query(None, description="Filter by showroom"),
    is_active: bool = Query(None, description="Filter by active status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_showroom_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users (with filtering)
    
    Access:
    - Admin: Can see all users
    - Showroom Manager: Can only see users in their showroom
    """
    # Build query
    query = select(User)
    
    # Apply role-based filtering
    if current_user.role == UserRole.SHOWROOM:
        # Showroom managers can only see users in their showroom
        query = query.where(User.showroom_id == current_user.showroom_id)
    
    # Apply filters
    if role:
        query = query.where(User.role == role)
    if showroom_id:
        if current_user.role != UserRole.ADMIN and showroom_id != current_user.showroom_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access users from other showrooms"
            )
        query = query.where(User.showroom_id == showroom_id)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user by ID
    
    Access:
    - Admin: Can see any user
    - Showroom Manager: Can see users in their showroom
    - Others: Can only see themselves
    """
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access
    if current_user.role == UserRole.ADMIN:
        pass  # Admin can see anyone
    elif current_user.role == UserRole.SHOWROOM:
        if user.showroom_id != current_user.showroom_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    else:
        if user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user (admin only)
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate showroom_id for non-admin users
    if user_data.role in [UserRole.SHOWROOM, UserRole.MECHANIC]:
        if user_data.showroom_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Showroom ID required for showroom staff"
            )
    
    # Create user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        showroom_id=user_data.showroom_id,
        is_active=True,
        is_verified=False
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Log user creation
    audit_log = AuditLog(
        user_id=current_user.id,
        action="user_created",
        resource_type="user",
        resource_id=user.id,
        description=f"Created user: {user.email} with role: {user.role.value}",
        success="success"
    )
    db.add(audit_log)
    await db.commit()
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user (admin only)
    """
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.showroom_id is not None:
        user.showroom_id = user_data.showroom_id
    
    await db.commit()
    await db.refresh(user)
    
    # Log update
    audit_log = AuditLog(
        user_id=current_user.id,
        action="user_updated",
        resource_type="user",
        resource_id=user.id,
        description=f"Updated user: {user.email}",
        success="success"
    )
    db.add(audit_log)
    await db.commit()
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user (admin only)
    
    Note: This is a soft delete (sets is_active = False)
    """
    # Fetch user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Soft delete
    user.is_active = False
    await db.commit()
    
    # Log deletion
    audit_log = AuditLog(
        user_id=current_user.id,
        action="user_deleted",
        resource_type="user",
        resource_id=user.id,
        description=f"Deleted user: {user.email}",
        success="success"
    )
    db.add(audit_log)
    await db.commit()
    
    return None
