"""
Vehicle schemas for API validation
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.vehicle import VehicleStatus


class VehicleBase(BaseModel):
    """Base vehicle schema"""
    registration_number: str = Field(..., min_length=1, max_length=50)
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    variant: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle"""
    vin: Optional[str] = Field(None, min_length=17, max_length=17)
    owner_id: int
    home_showroom_id: int
    current_mileage: Optional[float] = Field(None, ge=0)


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle"""
    current_mileage: Optional[float] = Field(None, ge=0)
    health_status: Optional[VehicleStatus] = None
    health_score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class VehicleResponse(VehicleBase):
    """Schema for vehicle API responses"""
    id: int
    vin: Optional[str]
    owner_id: int
    home_showroom_id: int
    current_mileage: Optional[float]
    health_status: VehicleStatus
    health_score: Optional[float]
    last_service_date: Optional[datetime]
    next_service_due: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
