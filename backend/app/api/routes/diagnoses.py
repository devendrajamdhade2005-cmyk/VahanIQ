"""
Diagnosis API endpoints
Orchestrates ML, RAG, and LLM for complete vehicle diagnosis
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_mechanic
from app.models.user import User
from app.models.diagnosis import Diagnosis
from app.models.vehicle import Vehicle
from app.schemas.diagnosis import (
    DiagnosisCreate,
    DiagnosisUpdate,
    CompleteDiagnosisResponse,
    DiagnosisDetailResponse,
    RegenerateGuideRequest,
    RepairGuide,
    DiagnosisListResponse,
    DiagnosisStatsResponse
)
from app.services.diagnosis_service import get_diagnosis_service

router = APIRouter()


@router.post("/", response_model=CompleteDiagnosisResponse, status_code=status.HTTP_201_CREATED)
async def create_diagnosis(
    request: DiagnosisCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mechanic())
):
    """
    Create AI-powered diagnosis
    
    Orchestrates:
    1. ML prediction from sensor data
    2. RAG context retrieval (manuals + similar cases)
    3. LLM repair guide generation
    
    Returns complete diagnosis with actionable repair guide
    """
    diagnosis_service = get_diagnosis_service()
    
    try:
        result = await diagnosis_service.create_diagnosis(
            db=db,
            vehicle_id=request.vehicle_id,
            current_user=current_user,
            notes=request.notes,
            generate_repair_guide=request.generate_repair_guide
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Diagnosis creation failed: {str(e)}"
        )


@router.get("/", response_model=List[DiagnosisListResponse])
async def list_diagnoses(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    vehicle_id: Optional[int] = None,
    failure_type: Optional[str] = None,
    severity: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List diagnoses with filters
    
    Access control:
    - Admin: All diagnoses
    - Showroom/Mechanic: Showroom diagnoses only
    - Owner: Own vehicle diagnoses only
    """
    query = select(Diagnosis).join(Vehicle, Diagnosis.vehicle_id == Vehicle.id)
    
    # Apply role-based filtering
    if current_user.role == "owner":
        query = query.where(Vehicle.owner_id == current_user.id)
    elif current_user.role in ["showroom_manager", "mechanic"]:
        if current_user.showroom_id:
            query = query.where(Vehicle.showroom_id == current_user.showroom_id)
    
    # Apply filters
    filters = []
    if vehicle_id:
        filters.append(Diagnosis.vehicle_id == vehicle_id)
    if failure_type:
        filters.append(Diagnosis.failure_type == failure_type)
    if severity:
        filters.append(Diagnosis.severity == severity)
    if status_filter:
        filters.append(Diagnosis.status == status_filter)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by created date, newest first
    query = query.order_by(Diagnosis.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(query)
    diagnoses = result.scalars().all()
    
    # Format response
    response = []
    for diagnosis in diagnoses:
        # Get vehicle
        vehicle_query = select(Vehicle).where(Vehicle.id == diagnosis.vehicle_id)
        vehicle_result = await db.execute(vehicle_query)
        vehicle = vehicle_result.scalar_one_or_none()
        
        # Get mechanic
        mechanic_query = select(User).where(User.id == diagnosis.mechanic_id)
        mechanic_result = await db.execute(mechanic_query)
        mechanic = mechanic_result.scalar_one_or_none()
        
        response.append(DiagnosisListResponse(
            id=diagnosis.id,
            vehicle_id=diagnosis.vehicle_id,
            vehicle_info=f"{vehicle.make} {vehicle.model} ({vehicle.year})" if vehicle else "Unknown",
            failure_type=diagnosis.failure_type,
            confidence_score=diagnosis.confidence_score,
            severity=diagnosis.severity,
            status=diagnosis.status,
            estimated_repair_cost=diagnosis.estimated_repair_cost,
            estimated_repair_hours=diagnosis.estimated_repair_hours,
            created_at=diagnosis.created_at.isoformat(),
            mechanic_name=mechanic.full_name if mechanic else "Unknown"
        ))
    
    return response


@router.get("/{diagnosis_id}", response_model=DiagnosisDetailResponse)
async def get_diagnosis(
    diagnosis_id: int,
    include_full_context: bool = Query(False, description="Include full RAG context"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get diagnosis details
    
    Returns complete diagnosis with ML prediction, RAG context, and repair guide
    """
    diagnosis_service = get_diagnosis_service()
    
    try:
        result = await diagnosis_service.get_diagnosis_details(
            db=db,
            diagnosis_id=diagnosis_id,
            include_full_context=include_full_context
        )
        
        # Access control check
        vehicle_id = result["diagnosis"]["vehicle_id"]
        vehicle_query = select(Vehicle).where(Vehicle.id == vehicle_id)
        vehicle_result = await db.execute(vehicle_query)
        vehicle = vehicle_result.scalar_one_or_none()
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found"
            )
        
        # Check access
        if current_user.role == "owner" and vehicle.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        elif current_user.role in ["showroom_manager", "mechanic"]:
            if current_user.showroom_id and vehicle.showroom_id != current_user.showroom_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get diagnosis: {str(e)}"
        )


@router.put("/{diagnosis_id}", response_model=DiagnosisDetailResponse)
async def update_diagnosis(
    diagnosis_id: int,
    update: DiagnosisUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mechanic())
):
    """
    Update diagnosis
    
    Allows mechanic to update description, status, and provide feedback
    """
    query = select(Diagnosis).where(Diagnosis.id == diagnosis_id)
    result = await db.execute(query)
    diagnosis = result.scalar_one_or_none()
    
    if not diagnosis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnosis not found"
        )
    
    # Update fields
    update_data = update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(diagnosis, field, value)
    
    await db.commit()
    await db.refresh(diagnosis)
    
    # Return updated diagnosis
    diagnosis_service = get_diagnosis_service()
    return await diagnosis_service.get_diagnosis_details(db=db, diagnosis_id=diagnosis_id)


@router.post("/{diagnosis_id}/regenerate-guide", response_model=RepairGuide)
async def regenerate_repair_guide(
    diagnosis_id: int,
    request: RegenerateGuideRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_mechanic())
):
    """
    Regenerate repair guide for existing diagnosis
    
    Useful when mechanic wants to:
    - Add custom notes
    - Get updated repair steps
    - Regenerate with new context
    """
    diagnosis_service = get_diagnosis_service()
    
    try:
        repair_guide = await diagnosis_service.regenerate_repair_guide(
            db=db,
            diagnosis_id=diagnosis_id,
            custom_notes=request.custom_notes
        )
        
        return repair_guide
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate guide: {str(e)}"
        )


@router.get("/stats/overview", response_model=DiagnosisStatsResponse)
async def get_diagnosis_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get diagnosis statistics
    
    Returns aggregated stats for dashboard
    """
    from datetime import datetime, timedelta
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = select(Diagnosis).where(Diagnosis.created_at >= start_date)
    
    # Apply role-based filtering
    if current_user.role == "owner":
        query = query.join(Vehicle).where(Vehicle.owner_id == current_user.id)
    elif current_user.role in ["showroom_manager", "mechanic"]:
        if current_user.showroom_id:
            query = query.join(Vehicle).where(Vehicle.showroom_id == current_user.showroom_id)
    
    result = await db.execute(query)
    diagnoses = result.scalars().all()
    
    # Calculate stats
    total = len(diagnoses)
    
    by_failure_type = {}
    by_severity = {}
    by_status = {}
    total_confidence = 0
    
    for diagnosis in diagnoses:
        # Failure type
        by_failure_type[diagnosis.failure_type] = by_failure_type.get(diagnosis.failure_type, 0) + 1
        
        # Severity
        by_severity[diagnosis.severity] = by_severity.get(diagnosis.severity, 0) + 1
        
        # Status
        by_status[diagnosis.status] = by_status.get(diagnosis.status, 0) + 1
        
        # Confidence
        total_confidence += diagnosis.confidence_score
    
    avg_confidence = total_confidence / total if total > 0 else 0
    
    # Accuracy stats (from feedback)
    feedback_count = sum(1 for d in diagnoses if d.accuracy_rating is not None)
    avg_rating = sum(d.accuracy_rating for d in diagnoses if d.accuracy_rating) / feedback_count if feedback_count > 0 else None
    
    return DiagnosisStatsResponse(
        total_diagnoses=total,
        by_failure_type=by_failure_type,
        by_severity=by_severity,
        by_status=by_status,
        average_confidence=avg_confidence,
        accuracy_stats={
            "feedback_count": feedback_count,
            "average_rating": avg_rating
        } if avg_rating else None
    )
