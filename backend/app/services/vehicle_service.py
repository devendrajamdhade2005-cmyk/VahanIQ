"""
Vehicle service - Business logic for vehicle operations
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from fastapi import HTTPException, status
from datetime import datetime

from app.models.vehicle import Vehicle, VehicleStatus
from app.models.user import User, UserRole
from app.models.audit import AuditLog


class VehicleService:
    """Vehicle management service"""
    
    @staticmethod
    async def get_vehicles(
        db: AsyncSession,
        current_user: User,
        skip: int = 0,
        limit: int = 100,
        status: Optional[VehicleStatus] = None,
        showroom_id: Optional[int] = None,
        search: Optional[str] = None
    ) -> List[Vehicle]:
        """
        Get vehicles with role-based filtering
        
        - Admin: Can see all vehicles
        - Showroom/Mechanic: Only vehicles in their showroom
        - Owner: Only their own vehicles
        """
        query = select(Vehicle)
        
        # Apply role-based filtering
        if current_user.role == UserRole.ADMIN:
            # Admin can see all
            pass
        elif current_user.role in [UserRole.SHOWROOM, UserRole.MECHANIC]:
            # Showroom staff can only see vehicles in their showroom
            query = query.where(Vehicle.home_showroom_id == current_user.showroom_id)
        elif current_user.role == UserRole.OWNER:
            # Owners can only see their own vehicles
            query = query.where(Vehicle.owner_id == current_user.id)
        
        # Apply filters
        if status:
            query = query.where(Vehicle.health_status == status)
        
        if showroom_id:
            # Verify access
            if current_user.role in [UserRole.SHOWROOM, UserRole.MECHANIC]:
                if showroom_id != current_user.showroom_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Cannot access vehicles from other showrooms"
                    )
            query = query.where(Vehicle.home_showroom_id == showroom_id)
        
        if search:
            # Search by registration, VIN, make, or model
            search_pattern = f"%{search}%"
            query = query.where(
                or_(
                    Vehicle.registration_number.ilike(search_pattern),
                    Vehicle.vin.ilike(search_pattern),
                    Vehicle.make.ilike(search_pattern),
                    Vehicle.model.ilike(search_pattern)
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        vehicles = result.scalars().all()
        
        return vehicles
    
    @staticmethod
    async def get_vehicle_by_id(
        db: AsyncSession,
        vehicle_id: int,
        current_user: User
    ) -> Vehicle:
        """Get vehicle by ID with access control"""
        result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
        vehicle = result.scalar_one_or_none()
        
        if vehicle is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check access
        await VehicleService._verify_vehicle_access(vehicle, current_user)
        
        return vehicle
    
    @staticmethod
    async def create_vehicle(
        db: AsyncSession,
        vehicle_data: dict,
        current_user: User
    ) -> Vehicle:
        """Create a new vehicle"""
        # Verify registration number doesn't exist
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.registration_number == vehicle_data["registration_number"]
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle with this registration number already exists"
            )
        
        # Verify VIN if provided
        if vehicle_data.get("vin"):
            result = await db.execute(
                select(Vehicle).where(Vehicle.vin == vehicle_data["vin"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Vehicle with this VIN already exists"
                )
        
        # Create vehicle
        vehicle = Vehicle(**vehicle_data)
        db.add(vehicle)
        await db.commit()
        await db.refresh(vehicle)
        
        # Log creation
        audit_log = AuditLog(
            user_id=current_user.id,
            action="vehicle_created",
            resource_type="vehicle",
            resource_id=vehicle.id,
            description=f"Created vehicle: {vehicle.registration_number}",
            success="success"
        )
        db.add(audit_log)
        await db.commit()
        
        return vehicle
    
    @staticmethod
    async def update_vehicle(
        db: AsyncSession,
        vehicle_id: int,
        update_data: dict,
        current_user: User
    ) -> Vehicle:
        """Update vehicle"""
        vehicle = await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        # Update fields
        for field, value in update_data.items():
            if value is not None and hasattr(vehicle, field):
                setattr(vehicle, field, value)
        
        await db.commit()
        await db.refresh(vehicle)
        
        # Log update
        audit_log = AuditLog(
            user_id=current_user.id,
            action="vehicle_updated",
            resource_type="vehicle",
            resource_id=vehicle.id,
            description=f"Updated vehicle: {vehicle.registration_number}",
            success="success"
        )
        db.add(audit_log)
        await db.commit()
        
        return vehicle
    
    @staticmethod
    async def delete_vehicle(
        db: AsyncSession,
        vehicle_id: int,
        current_user: User
    ):
        """Delete vehicle (admin only)"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete vehicles"
            )
        
        vehicle = await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
        
        # Log deletion before removing
        audit_log = AuditLog(
            user_id=current_user.id,
            action="vehicle_deleted",
            resource_type="vehicle",
            resource_id=vehicle.id,
            description=f"Deleted vehicle: {vehicle.registration_number}",
            success="success"
        )
        db.add(audit_log)
        
        await db.delete(vehicle)
        await db.commit()
    
    @staticmethod
    async def _verify_vehicle_access(vehicle: Vehicle, current_user: User):
        """Verify user has access to vehicle"""
        if current_user.role == UserRole.ADMIN:
            return  # Admin can access all
        
        if current_user.role == UserRole.OWNER:
            if vehicle.owner_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this vehicle"
                )
        
        if current_user.role in [UserRole.SHOWROOM, UserRole.MECHANIC]:
            if vehicle.home_showroom_id != current_user.showroom_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this vehicle"
                )
