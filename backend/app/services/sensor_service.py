"""
Sensor data service - OBD-II data ingestion and retrieval
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from fastapi import HTTPException, status

from app.models.sensor import SensorReading
from app.models.vehicle import Vehicle
from app.models.user import User, UserRole
from app.services.vehicle_service import VehicleService


class SensorService:
    """Sensor data management service"""
    
    @staticmethod
    async def ingest_sensor_reading(
        db: AsyncSession,
        vehicle_id: int,
        sensor_data: dict,
        current_user: User,
        timestamp: Optional[datetime] = None
    ) -> SensorReading:
        """
        Ingest a single sensor reading
        
        Access: Admin, or showroom staff for vehicles in their showroom
        """
        # Verify vehicle exists and user has access
        vehicle = await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        # Use provided timestamp or current time
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Create sensor reading
        reading = SensorReading(
            vehicle_id=vehicle_id,
            timestamp=timestamp,
            **sensor_data
        )
        
        db.add(reading)
        
        # Update vehicle mileage if provided
        if sensor_data.get("mileage"):
            vehicle.current_mileage = sensor_data["mileage"]
        
        await db.commit()
        await db.refresh(reading)
        
        return reading
    
    @staticmethod
    async def ingest_bulk_readings(
        db: AsyncSession,
        vehicle_id: int,
        readings: List[dict],
        current_user: User
    ) -> int:
        """
        Bulk ingest sensor readings for a vehicle
        
        Returns: Number of readings ingested
        """
        # Verify vehicle access
        vehicle = await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        # Create all readings
        sensor_readings = []
        latest_mileage = vehicle.current_mileage or 0
        
        for reading_data in readings:
            timestamp = reading_data.get("timestamp", datetime.utcnow())
            
            reading = SensorReading(
                vehicle_id=vehicle_id,
                timestamp=timestamp,
                **{k: v for k, v in reading_data.items() if k != "timestamp"}
            )
            sensor_readings.append(reading)
            
            # Track latest mileage
            if reading_data.get("mileage") and reading_data["mileage"] > latest_mileage:
                latest_mileage = reading_data["mileage"]
        
        db.add_all(sensor_readings)
        
        # Update vehicle mileage
        vehicle.current_mileage = latest_mileage
        
        await db.commit()
        
        return len(sensor_readings)
    
    @staticmethod
    async def get_vehicle_readings(
        db: AsyncSession,
        vehicle_id: int,
        current_user: User,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SensorReading]:
        """
        Get sensor readings for a vehicle
        
        If no time range specified, returns most recent readings
        """
        # Verify vehicle access
        await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        # Build query
        query = select(SensorReading).where(SensorReading.vehicle_id == vehicle_id)
        
        # Apply time filters
        if start_time:
            query = query.where(SensorReading.timestamp >= start_time)
        if end_time:
            query = query.where(SensorReading.timestamp <= end_time)
        
        # Order by timestamp descending and limit
        query = query.order_by(desc(SensorReading.timestamp)).limit(limit)
        
        result = await db.execute(query)
        readings = result.scalars().all()
        
        return readings
    
    @staticmethod
    async def get_latest_reading(
        db: AsyncSession,
        vehicle_id: int,
        current_user: User
    ) -> Optional[SensorReading]:
        """Get the most recent sensor reading for a vehicle"""
        # Verify vehicle access
        await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        query = select(SensorReading).where(
            SensorReading.vehicle_id == vehicle_id
        ).order_by(
            desc(SensorReading.timestamp)
        ).limit(1)
        
        result = await db.execute(query)
        reading = result.scalar_one_or_none()
        
        return reading
    
    @staticmethod
    async def get_sensor_statistics(
        db: AsyncSession,
        vehicle_id: int,
        current_user: User,
        parameter: str,
        hours: int = 24
    ) -> dict:
        """
        Get statistics for a specific sensor parameter over time
        
        Args:
            parameter: Sensor parameter name (e.g., "rpm", "coolant_temp")
            hours: Number of hours to look back
        """
        # Verify vehicle access
        await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Verify parameter exists in model
        if not hasattr(SensorReading, parameter):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sensor parameter: {parameter}"
            )
        
        # Get column
        column = getattr(SensorReading, parameter)
        
        # Query statistics
        query = select(
            func.min(column).label("min_value"),
            func.max(column).label("max_value"),
            func.avg(column).label("avg_value"),
            func.count(column).label("count")
        ).where(
            and_(
                SensorReading.vehicle_id == vehicle_id,
                SensorReading.timestamp >= start_time,
                SensorReading.timestamp <= end_time,
                column.isnot(None)
            )
        )
        
        result = await db.execute(query)
        stats = result.one_or_none()
        
        # Get latest value
        latest_query = select(column).where(
            SensorReading.vehicle_id == vehicle_id
        ).order_by(
            desc(SensorReading.timestamp)
        ).limit(1)
        
        latest_result = await db.execute(latest_query)
        latest_value = latest_result.scalar_one_or_none()
        
        if stats is None:
            return {
                "parameter": parameter,
                "min_value": None,
                "max_value": None,
                "avg_value": None,
                "latest_value": latest_value,
                "readings_count": 0,
                "time_range_hours": hours
            }
        
        return {
            "parameter": parameter,
            "min_value": float(stats[0]) if stats[0] is not None else None,
            "max_value": float(stats[1]) if stats[1] is not None else None,
            "avg_value": float(stats[2]) if stats[2] is not None else None,
            "latest_value": float(latest_value) if latest_value is not None else None,
            "readings_count": stats[3],
            "time_range_hours": hours
        }
    
    @staticmethod
    async def delete_old_readings(
        db: AsyncSession,
        vehicle_id: int,
        days_to_keep: int = 730  # 2 years default
    ) -> int:
        """
        Delete old sensor readings (data retention policy)
        
        Returns: Number of readings deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Delete old readings
        delete_query = select(SensorReading).where(
            and_(
                SensorReading.vehicle_id == vehicle_id,
                SensorReading.timestamp < cutoff_date
            )
        )
        
        result = await db.execute(delete_query)
        old_readings = result.scalars().all()
        
        count = len(old_readings)
        
        for reading in old_readings:
            await db.delete(reading)
        
        await db.commit()
        
        return count
