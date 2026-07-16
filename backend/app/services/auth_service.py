"""
Authentication service - Business logic for auth operations
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.models.user import User
from app.models.audit import AuditLog
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token


class AuthService:
    """Authentication service"""
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
        
        Returns:
            User object if authenticated, None otherwise
        """
        # Fetch user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user is None:
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return None
        
        # Check if account is active
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> dict:
        """
        Login user and generate tokens
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
        
        Returns:
            Dictionary with access_token, refresh_token, and user info
        
        Raises:
            HTTPException: If authentication fails
        """
        # Authenticate user
        user = await AuthService.authenticate_user(db, email, password)
        
        if user is None:
            # Log failed login attempt
            audit_log = AuditLog(
                action="login_failed",
                resource_type="user",
                description=f"Failed login attempt for email: {email}",
                success="failure"
            )
            db.add(audit_log)
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login timestamp
        user.last_login = datetime.utcnow()
        await db.commit()
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user.id, "role": user.role.value})
        refresh_token = create_refresh_token(data={"sub": user.id, "role": user.role.value})
        
        # Log successful login
        audit_log = AuditLog(
            user_id=user.id,
            action="login_success",
            resource_type="user",
            resource_id=user.id,
            description=f"User logged in: {user.email}",
            success="success"
        )
        db.add(audit_log)
        await db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "showroom_id": user.showroom_id,
                "is_active": user.is_active,
                "created_at": user.created_at
            }
        }
    
    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            db: Database session
            user: Current user
            current_password: Current password for verification
            new_password: New password to set
        
        Returns:
            True if successful
        
        Raises:
            HTTPException: If current password is incorrect
        """
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        
        # Log password change
        audit_log = AuditLog(
            user_id=user.id,
            action="password_changed",
            resource_type="user",
            resource_id=user.id,
            description="User changed their password",
            success="success"
        )
        db.add(audit_log)
        await db.commit()
        
        return True
    
    @staticmethod
    async def reset_password(
        db: AsyncSession,
        admin_user: User,
        email: str,
        new_password: str
    ) -> bool:
        """
        Reset user password (admin only)
        
        Args:
            db: Database session
            admin_user: Admin performing the reset
            email: Email of user to reset
            new_password: New password to set
        
        Returns:
            True if successful
        
        Raises:
            HTTPException: If user not found
        """
        # Fetch user
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        user.hashed_password = get_password_hash(new_password)
        await db.commit()
        
        # Log password reset
        audit_log = AuditLog(
            user_id=admin_user.id,
            action="password_reset",
            resource_type="user",
            resource_id=user.id,
            description=f"Admin {admin_user.email} reset password for {user.email}",
            success="success"
        )
        db.add(audit_log)
        await db.commit()
        
        return True
