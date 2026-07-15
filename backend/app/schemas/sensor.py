"""
Sensor reading schemas for OBD-II data
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SensorReadingBase(BaseModel):
    """Base sensor reading schema"""
    # Engine parameters
    rpm: Optional[float] = Field(None, ge=0, le=10000)
    speed: Optional[float] = Field(None, ge=0, le=300)
    engine_load: Optional[float] = Field(None, ge=0, le=100)
    coolant_temp: Optional[float] = Field(None, ge=-40, le=200)
    intake_temp: Optional[float] = Field(None, ge=-40, le=200)
    throttle_position: Optional[float] = Field(None, ge=0, le=100)
    maf: Optional[float] = Field(None, ge=0)
    
    # Fuel system
    fuel_pressure: Optional[float] = Field(None, ge=0)
    fuel_level: Optional[float] = Field(None, ge=0, le=100)
    fuel_trim_short: Optional[float] = Field(None, ge=-100, le=100)
    fuel_trim_long: Optional[float] = Field(None, ge=-100, le=100)
    
    # Emissions
    o2_voltage: Optional[float] = Field(None, ge=0, le=2)
    
    # Braking system
    brake_fluid_pressure: Optional[float] = Field(None, ge=0)
    brake_pad_thickness_fl: Optional[float] = Field(None, ge=0, le=50)
    brake_pad_thickness_fr: Optional[float] = Field(None, ge=0, le=50)
    brake_pad_thickness_rl: Optional[float] = Field(None, ge=0, le=50)
    brake_pad_thickness_rr: Optional[float] = Field(None, ge=0, le=50)
    
    # Transmission
    transmission_temp: Optional[float] = Field(None, ge=-40, le=200)
    gear_position: Optional[int] = Field(None, ge=-1, le=10)
    
    # Electrical
    battery_voltage: Optional[float] = Field(None, ge=0, le=20)
    
    # Diagnostic
    dtc_codes: Optional[str] = Field(None, max_length=500)
    
    # Mileage
    mileage: Optional[float] = Field(None, ge=0)


class SensorReadingCreate(SensorReadingBase):
    """Schema for creating a sensor reading"""
    vehicle_id: int
    timestamp: Optional[datetime] = None  # If not provided, use current time


class SensorReadingBulkCreate(BaseModel):
    """Schema for bulk sensor data ingestion"""
    vehicle_id: int
    readings: list[SensorReadingBase]


class SensorReadingResponse(SensorReadingBase):
    """Schema for sensor reading responses"""
    id: int
    vehicle_id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SensorStatistics(BaseModel):
    """Aggregated sensor statistics"""
    parameter: str
    min_value: Optional[float]
    max_value: Optional[float]
    avg_value: Optional[float]
    latest_value: Optional[float]
    readings_count: int
    
    
class VehicleHealthSummary(BaseModel):
    """Vehicle health summary based on sensor data"""
    vehicle_id: int
    registration_number: str
    health_status: str
    health_score: Optional[float]
    last_reading_time: Optional[datetime]
    total_readings: int
    critical_parameters: list[str] = []
    warnings: list[str] = []
