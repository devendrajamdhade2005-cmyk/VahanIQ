"""
Sensor reading model - Time-series OBD-II data
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SensorReading(Base):
    """Sensor reading model for OBD-II data"""
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Engine parameters
    rpm = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)  # km/h
    engine_load = Column(Float, nullable=True)  # percentage
    coolant_temp = Column(Float, nullable=True)  # Celsius
    intake_temp = Column(Float, nullable=True)  # Celsius
    throttle_position = Column(Float, nullable=True)  # percentage
    maf = Column(Float, nullable=True)  # Mass Air Flow (g/s)
    
    # Fuel system
    fuel_pressure = Column(Float, nullable=True)  # kPa
    fuel_level = Column(Float, nullable=True)  # percentage
    fuel_trim_short = Column(Float, nullable=True)  # percentage
    fuel_trim_long = Column(Float, nullable=True)  # percentage
    
    # Emissions
    o2_voltage = Column(Float, nullable=True)  # Volts
    
    # Braking system
    brake_fluid_pressure = Column(Float, nullable=True)  # bar
    brake_pad_thickness_fl = Column(Float, nullable=True)  # mm (front-left)
    brake_pad_thickness_fr = Column(Float, nullable=True)  # mm (front-right)
    brake_pad_thickness_rl = Column(Float, nullable=True)  # mm (rear-left)
    brake_pad_thickness_rr = Column(Float, nullable=True)  # mm (rear-right)
    
    # Transmission
    transmission_temp = Column(Float, nullable=True)  # Celsius
    gear_position = Column(Integer, nullable=True)
    
    # Electrical
    battery_voltage = Column(Float, nullable=True)  # Volts
    
    # Diagnostic Trouble Codes
    dtc_codes = Column(String(500), nullable=True)  # Comma-separated DTC codes
    
    # Mileage at reading
    mileage = Column(Float, nullable=True)  # km
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="sensor_readings")
    
    # Composite index for efficient time-series queries
    __table_args__ = (
        Index('ix_sensor_vehicle_timestamp', 'vehicle_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SensorReading(id={self.id}, vehicle_id={self.vehicle_id}, timestamp={self.timestamp})>"
