"""
Vehicle management routes
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.vehicle import VehicleStatus
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.services.vehicle_service import VehicleService

router = APIRouter()


@router.get("/", response_model=List[VehicleResponse])
async def get_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[VehicleStatus] = Query(None, description="Filter by health status"),
    showroom_id: Optional[int] = Query(None, description="Filter by showroom"),
    search: Optional[str] = Query(None, description="Search by registration, VIN, make, or model"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all vehicles with filtering
    
    Access control:
    - Admin: All vehicles
    - Showroom/Mechanic: Only vehicles in their showroom
    - Owner: Only their own vehicles
    """
    vehicles = await VehicleService.get_vehicles(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        status=status,
        showroom_id=showroom_id,
        search=search
    )
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get vehicle by ID
    
    Access control applied based on user role
    """
    vehicle = await VehicleService.get_vehicle_by_id(db, vehicle_id, current_user)
    return vehicle


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new vehicle (admin only)
    """
    vehicle = await VehicleService.create_vehicle(
        db=db,
        vehicle_data=vehicle_data.model_dump(),
        current_user=current_user
    )
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update vehicle
    
    Access: Admin or showroom staff for vehicles in their showroom
    """
    vehicle = await VehicleService.update_vehicle(
        db=db,
        vehicle_id=vehicle_id,
        update_data=vehicle_data.model_dump(exclude_unset=True),
        current_user=current_user
    )
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete vehicle (admin only)
    """
    await VehicleService.delete_vehicle(db, vehicle_id, current_user)
    return None
