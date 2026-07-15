"""
Audit log model for security and compliance
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """Audit log for tracking all administrative and sensitive actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Nullable for system actions
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., "user_created", "vehicle_updated", "diagnosis_confirmed"
    resource_type = Column(String(50), nullable=False, index=True)  # e.g., "user", "vehicle", "repair_case"
    resource_id = Column(Integer, nullable=True, index=True)  # ID of the affected resource
    
    # Context
    description = Column(Text, nullable=True)
    changes = Column(JSON, nullable=True)  # JSON object with before/after values
    
    # Request metadata
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(255), nullable=True)  # API endpoint called
    
    # Status
    success = Column(String(20), default="success", nullable=False)  # success, failure, error
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, resource={self.resource_type}:{self.resource_id})>"
