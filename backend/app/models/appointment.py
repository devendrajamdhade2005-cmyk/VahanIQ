"""
Appointment booking model
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class AppointmentStatus(str, enum.Enum):
    """Appointment status"""
    REQUESTED = "requested"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Appointment(Base):
    """Appointment booking model"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False, index=True)
    
    # Appointment details
    appointment_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., APT-2024-001234
    requested_date = Column(DateTime(timezone=True), nullable=False, index=True)
    confirmed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Service type
    service_type = Column(String(100), nullable=False)  # e.g., "Routine Maintenance", "Diagnosis", "Repair"
    reason = Column(Text, nullable=True)  # Customer's description of the issue
    
    # Status
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.REQUESTED, nullable=False, index=True)
    
    # Contact preferences
    preferred_contact_method = Column(String(20), nullable=True)  # phone, email, sms
    reminder_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    customer_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="appointments")
    showroom = relationship("Showroom", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, number={self.appointment_number}, status={self.status})>"
