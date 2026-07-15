"""
User model - Authentication and role management
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    SHOWROOM = "showroom"
    MECHANIC = "mechanic"
    OWNER = "owner"


class User(Base):
    """User model for authentication and access control"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    
    # Multi-tenancy: showroom_id for scoping access
    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=True, index=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    showroom = relationship("Showroom", back_populates="users")
    owned_vehicles = relationship("Vehicle", back_populates="owner", foreign_keys="Vehicle.owner_id")
    assigned_repairs = relationship("RepairCase", back_populates="technician", foreign_keys="RepairCase.technician_id")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
