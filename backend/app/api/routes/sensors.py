"""
Sensor data ingestion and retrieval routes
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.sensor import (
    SensorReadingCreate,
    SensorReadingBulkCreate,
    SensorReadingResponse,
)
from app.services.sensor_service import SensorService

router = APIRouter()


@router.post("/{vehicle_id}/sensors", response_model=SensorReadingResponse, status_code=status.HTTP_201_CREATED)
async def ingest_sensor_reading(
    vehicle_id: int,
    reading_data: SensorReadingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingest a single sensor reading for a vehicle
    
    Access: Admin, or showroom staff for vehicles in their showroom
    """
    reading = await SensorService.ingest_sensor_reading(
        db=db,
        vehicle_id=vehicle_id,
        sensor_data=reading_data.model_dump(exclude={"vehicle_id", "timestamp"}, exclude_unset=True),
        current_user=current_user,
        timestamp=reading_data.timestamp
    )
    return reading


@router.post("/{vehicle_id}/sensors/bulk", status_code=status.HTTP_201_CREATED)
async def ingest_bulk_sensor_readings(
    vehicle_id: int,
    bulk_data: List[SensorReadingCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Bulk ingest sensor readings for a vehicle
    
    Useful for:
    - Uploading historical data
    - Batch processing from OBD-II devices
    - Syncing offline data
    """
    readings_data = [
        reading.model_dump(exclude={"vehicle_id"}, exclude_unset=True)
        for reading in bulk_data
    ]
    
    count = await SensorService.ingest_bulk_readings(
        db=db,
        vehicle_id=vehicle_id,
        readings=readings_data,
        current_user=current_user
    )
    
    return {
        "message": f"Successfully ingested {count} sensor readings",
        "vehicle_id": vehicle_id,
        "readings_count": count
    }


@router.get("/{vehicle_id}/sensors", response_model=List[SensorReadingResponse])
async def get_vehicle_sensor_readings(
    vehicle_id: int,
    start_time: Optional[datetime] = Query(None, description="Filter readings from this time"),
    end_time: Optional[datetime] = Query(None, description="Filter readings until this time"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of readings to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sensor readings for a vehicle
    
    If no time range specified, returns most recent readings
    """
    readings = await SensorService.get_vehicle_readings(
        db=db,
        vehicle_id=vehicle_id,
        current_user=current_user,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )
    return readings


@router.get("/{vehicle_id}/sensors/latest", response_model=Optional[SensorReadingResponse])
async def get_latest_sensor_reading(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the most recent sensor reading for a vehicle
    """
    reading = await SensorService.get_latest_reading(
        db=db,
        vehicle_id=vehicle_id,
        current_user=current_user
    )
    return reading


@router.get("/{vehicle_id}/sensors/statistics/{parameter}")
async def get_sensor_statistics(
    vehicle_id: int,
    parameter: str,
    hours: int = Query(24, ge=1, le=168, description="Hours to look back (max 7 days)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get statistics for a specific sensor parameter
    
    Common parameters:
    - rpm, speed, engine_load
    - coolant_temp, intake_temp
    - fuel_level, fuel_pressure
    - brake_pad_thickness_fl, brake_pad_thickness_fr
    - battery_voltage
    """
    stats = await SensorService.get_sensor_statistics(
        db=db,
        vehicle_id=vehicle_id,
        current_user=current_user,
        parameter=parameter,
        hours=hours
    )
    return stats
