"""
Showroom/Service Center model
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Showroom(Base):
    """Showroom/Service Center model"""
    __tablename__ = "showrooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # Unique identifier
    
    # Contact information
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    
    # Operational details
    region = Column(String(100), nullable=True)
    manager_name = Column(String(255), nullable=True)
    capacity = Column(Integer, default=10, nullable=False)  # Max concurrent repairs
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="showroom")
    vehicles = relationship("Vehicle", back_populates="home_showroom")
    repair_cases = relationship("RepairCase", back_populates="showroom")
    parts = relationship("Part", back_populates="showroom")
    appointments = relationship("Appointment", back_populates="showroom")
    
    def __repr__(self):
        return f"<Showroom(id={self.id}, name={self.name}, code={self.code})>"
