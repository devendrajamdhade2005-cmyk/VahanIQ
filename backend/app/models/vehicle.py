"""
Vehicle model - Core entity for the platform
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class VehicleStatus(str, enum.Enum):
    """Vehicle health status"""
    HEALTHY = "healthy"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"


class Vehicle(Base):
    """Vehicle model"""
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    
    # Vehicle identification
    vin = Column(String(17), unique=True, nullable=True, index=True)  # Vehicle Identification Number
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Vehicle details
    make = Column(String(100), nullable=False)  # e.g., Tata
    model = Column(String(100), nullable=False)  # e.g., Nexon
    year = Column(Integer, nullable=False)
    variant = Column(String(100), nullable=True)  # e.g., XZ+ Diesel
    color = Column(String(50), nullable=True)
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    home_showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False, index=True)
    
    # Current status
    current_mileage = Column(Float, nullable=True)  # in km
    health_status = Column(SQLEnum(VehicleStatus), default=VehicleStatus.HEALTHY, nullable=False, index=True)
    health_score = Column(Float, nullable=True)  # 0-100 scale
    last_service_date = Column(DateTime(timezone=True), nullable=True)
    next_service_due = Column(DateTime(timezone=True), nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    owner = relationship("User", back_populates="owned_vehicles", foreign_keys=[owner_id])
    home_showroom = relationship("Showroom", back_populates="vehicles")
    sensor_readings = relationship("SensorReading", back_populates="vehicle", cascade="all, delete-orphan")
    diagnoses = relationship("Diagnosis", back_populates="vehicle", cascade="all, delete-orphan")
    repair_cases = relationship("RepairCase", back_populates="vehicle", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="vehicle", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehicle(id={self.id}, reg={self.registration_number}, make={self.make}, model={self.model})>"
