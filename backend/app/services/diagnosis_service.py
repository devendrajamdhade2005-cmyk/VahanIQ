"""
Diagnosis service - Orchestrates ML, RAG, and LLM for complete diagnosis
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.vehicle import Vehicle
from app.models.sensor import SensorReading
from app.models.diagnosis import Diagnosis
from app.models.user import User
from app.ml.predictor import get_predictor
from app.rag.retrieval_service import get_retrieval_service
from app.services.llm_service import get_llm_service

logger = logging.getLogger(__name__)


class DiagnosisService:
    """
    Complete diagnosis service orchestrating AI components
    Flow: Vehicle Data → ML Prediction → RAG Context → LLM Guide
    """
    
    def __init__(self):
        """Initialize diagnosis service"""
        self.ml_predictor = get_predictor()
        self.rag_service = get_retrieval_service()
        self.llm_service = get_llm_service()
    
    async def create_diagnosis(
        self,
        db: AsyncSession,
        vehicle_id: int,
        current_user: User,
        notes: Optional[str] = None,
        generate_repair_guide: bool = True
    ) -> Dict[str, Any]:
        """
        Create complete AI diagnosis for a vehicle
        
        Args:
            db: Database session
            vehicle_id: Vehicle to diagnose
            current_user: User creating diagnosis
            notes: Optional mechanic notes
            generate_repair_guide: Whether to generate LLM repair guide
            
        Returns:
            Complete diagnosis with ML prediction, RAG context, and LLM guide
        """
        logger.info(f"Creating diagnosis for vehicle {vehicle_id}")
        
        # 1. Get vehicle and latest sensor data
        vehicle = await self._get_vehicle(db, vehicle_id)
        sensor_data = await self._get_latest_sensor_data(db, vehicle_id)
        
        if not sensor_data:
            raise ValueError("No sensor data available for diagnosis")
        
        # 2. ML Prediction
        logger.info("Running ML prediction...")
        ml_prediction = self.ml_predictor.predict_failure(sensor_data)
        
        failure_type = ml_prediction["failure_type"]
        probability = ml_prediction["probability"]
        severity = ml_prediction["severity"]
        
        # 3. RAG Context Retrieval
        logger.info("Retrieving RAG context...")
        rag_context = await self.rag_service.get_repair_context(
            db=db,
            failure_type=failure_type,
            diagnosis_description=ml_prediction["explanation"],
            vehicle_make=vehicle.make,
            vehicle_model=vehicle.model,
            dtc_codes=sensor_data.get("dtc_codes", "").split(",") if sensor_data.get("dtc_codes") else None
        )
        
        # 4. LLM Repair Guide Generation (if requested)
        repair_guide = None
        customer_summary = None
        
        if generate_repair_guide and probability > 0.3:  # Only generate if confidence > 30%
            logger.info("Generating LLM repair guide...")
            
            vehicle_info = {
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "mileage": vehicle.mileage,
                "registration_number": vehicle.registration_number
            }
            
            try:
                repair_guide = await self.llm_service.generate_repair_guide(
                    vehicle_info=vehicle_info,
                    ml_prediction=ml_prediction,
                    rag_context=rag_context,
                    diagnosis_description=notes
                )
                
                # Generate customer-friendly summary
                customer_summary = await self.llm_service.generate_diagnosis_summary(
                    vehicle_info=vehicle_info,
                    sensor_data=sensor_data,
                    ml_prediction=ml_prediction
                )
                
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                # Continue without LLM guide
                repair_guide = None
                customer_summary = None
        
        # 5. Save diagnosis to database
        diagnosis = Diagnosis(
            vehicle_id=vehicle_id,
            mechanic_id=current_user.id,
            failure_type=failure_type,
            confidence_score=probability,
            severity=severity,
            ml_explanation=ml_prediction["explanation"],
            top_contributing_features=ml_prediction.get("top_features", []),
            description=notes or ml_prediction["explanation"],
            recommended_actions=repair_guide.get("diagnosis_summary") if repair_guide else ml_prediction["explanation"],
            estimated_repair_cost=repair_guide.get("estimated_total_cost_inr") if repair_guide else None,
            estimated_repair_hours=repair_guide.get("estimated_labor_hours") if repair_guide else None,
            status="pending"
        )
        
        db.add(diagnosis)
        await db.commit()
        await db.refresh(diagnosis)
        
        logger.info(f"Diagnosis created: ID={diagnosis.id}, Type={failure_type}, Confidence={probability:.2f}")
        
        # 6. Return complete diagnosis package
        return {
            "diagnosis": {
                "id": diagnosis.id,
                "vehicle_id": vehicle_id,
                "failure_type": failure_type,
                "confidence_score": probability,
                "severity": severity,
                "status": diagnosis.status,
                "created_at": diagnosis.created_at.isoformat()
            },
            "vehicle": {
                "id": vehicle.id,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "registration_number": vehicle.registration_number,
                "mileage": vehicle.mileage,
                "health_status": vehicle.health_status
            },
            "ml_prediction": ml_prediction,
            "rag_context": {
                "knowledge_articles_count": len(rag_context.get("knowledge_articles", [])),
                "similar_cases_count": len(rag_context.get("similar_cases", [])),
                "knowledge_articles": rag_context.get("knowledge_articles", [])[:3],  # Top 3
                "similar_cases": rag_context.get("similar_cases", [])[:3]  # Top 3
            },
            "repair_guide": repair_guide,
            "customer_summary": customer_summary,
            "sensor_data_timestamp": sensor_data.get("timestamp")
        }
    
    async def get_diagnosis_details(
        self,
        db: AsyncSession,
        diagnosis_id: int,
        include_full_context: bool = False
    ) -> Dict[str, Any]:
        """
        Get complete diagnosis details with all AI insights
        
        Args:
            db: Database session
            diagnosis_id: Diagnosis ID
            include_full_context: Include full RAG context (not just summary)
            
        Returns:
            Complete diagnosis details
        """
        # Get diagnosis from DB
        query = select(Diagnosis).where(Diagnosis.id == diagnosis_id)
        result = await db.execute(query)
        diagnosis = result.scalar_one_or_none()
        
        if not diagnosis:
            raise ValueError(f"Diagnosis {diagnosis_id} not found")
        
        # Get vehicle
        vehicle = await self._get_vehicle(db, diagnosis.vehicle_id)
        
        # Get sensor data used for diagnosis
        sensor_data = await self._get_sensor_data_at_time(
            db,
            diagnosis.vehicle_id,
            diagnosis.created_at
        )
        
        response = {
            "diagnosis": {
                "id": diagnosis.id,
                "vehicle_id": diagnosis.vehicle_id,
                "failure_type": diagnosis.failure_type,
                "confidence_score": diagnosis.confidence_score,
                "severity": diagnosis.severity,
                "description": diagnosis.description,
                "recommended_actions": diagnosis.recommended_actions,
                "estimated_repair_cost": diagnosis.estimated_repair_cost,
                "estimated_repair_hours": diagnosis.estimated_repair_hours,
                "status": diagnosis.status,
                "created_at": diagnosis.created_at.isoformat(),
                "ml_explanation": diagnosis.ml_explanation,
                "top_features": diagnosis.top_contributing_features
            },
            "vehicle": {
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "registration_number": vehicle.registration_number,
                "mileage": vehicle.mileage
            },
            "sensor_data": sensor_data
        }
        
        # Include full RAG context if requested
        if include_full_context and diagnosis.failure_type:
            rag_context = await self.rag_service.get_repair_context(
                db=db,
                failure_type=diagnosis.failure_type,
                diagnosis_description=diagnosis.description,
                vehicle_make=vehicle.make,
                vehicle_model=vehicle.model,
                dtc_codes=None
            )
            response["rag_context"] = rag_context
        
        return response
    
    async def regenerate_repair_guide(
        self,
        db: AsyncSession,
        diagnosis_id: int,
        custom_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Regenerate repair guide for existing diagnosis with optional custom notes
        
        Args:
            db: Database session
            diagnosis_id: Diagnosis to regenerate guide for
            custom_notes: Optional custom notes to incorporate
            
        Returns:
            New repair guide
        """
        # Get diagnosis
        query = select(Diagnosis).where(Diagnosis.id == diagnosis_id)
        result = await db.execute(query)
        diagnosis = result.scalar_one_or_none()
        
        if not diagnosis:
            raise ValueError(f"Diagnosis {diagnosis_id} not found")
        
        # Get vehicle
        vehicle = await self._get_vehicle(db, diagnosis.vehicle_id)
        
        # Get RAG context
        rag_context = await self.rag_service.get_repair_context(
            db=db,
            failure_type=diagnosis.failure_type,
            diagnosis_description=diagnosis.description,
            vehicle_make=vehicle.make,
            vehicle_model=vehicle.model,
            dtc_codes=None
        )
        
        # Reconstruct ML prediction format
        ml_prediction = {
            "failure_type": diagnosis.failure_type,
            "probability": diagnosis.confidence_score,
            "severity": diagnosis.severity,
            "explanation": diagnosis.ml_explanation,
            "top_features": diagnosis.top_contributing_features or []
        }
        
        vehicle_info = {
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "mileage": vehicle.mileage,
            "registration_number": vehicle.registration_number
        }
        
        # Generate new guide
        repair_guide = await self.llm_service.generate_repair_guide(
            vehicle_info=vehicle_info,
            ml_prediction=ml_prediction,
            rag_context=rag_context,
            diagnosis_description=custom_notes or diagnosis.description
        )
        
        # Update diagnosis with new estimates
        if repair_guide:
            diagnosis.estimated_repair_cost = repair_guide.get("estimated_total_cost_inr")
            diagnosis.estimated_repair_hours = repair_guide.get("estimated_labor_hours")
            await db.commit()
        
        return repair_guide
    
    async def _get_vehicle(self, db: AsyncSession, vehicle_id: int) -> Vehicle:
        """Get vehicle from database"""
        query = select(Vehicle).where(Vehicle.id == vehicle_id)
        result = await db.execute(query)
        vehicle = result.scalar_one_or_none()
        
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        return vehicle
    
    async def _get_latest_sensor_data(
        self,
        db: AsyncSession,
        vehicle_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get latest sensor reading for vehicle"""
        query = select(SensorReading).where(
            SensorReading.vehicle_id == vehicle_id
        ).order_by(SensorReading.timestamp.desc()).limit(1)
        
        result = await db.execute(query)
        sensor_reading = result.scalar_one_or_none()
        
        if not sensor_reading:
            return None
        
        # Convert to dict format expected by ML model
        return {
            "rpm": sensor_reading.rpm,
            "speed": sensor_reading.speed,
            "engine_load": sensor_reading.engine_load,
            "coolant_temp": sensor_reading.coolant_temp,
            "intake_temp": sensor_reading.intake_temp,
            "throttle_position": sensor_reading.throttle_position,
            "maf": sensor_reading.maf,
            "fuel_pressure": sensor_reading.fuel_pressure,
            "fuel_level": sensor_reading.fuel_level,
            "fuel_trim_short": sensor_reading.fuel_trim_short,
            "fuel_trim_long": sensor_reading.fuel_trim_long,
            "o2_voltage": sensor_reading.o2_voltage,
            "brake_pad_thickness_fl": sensor_reading.brake_pad_thickness_fl,
            "brake_pad_thickness_fr": sensor_reading.brake_pad_thickness_fr,
            "brake_pad_thickness_rl": sensor_reading.brake_pad_thickness_rl,
            "brake_pad_thickness_rr": sensor_reading.brake_pad_thickness_rr,
            "brake_fluid_pressure": sensor_reading.brake_fluid_pressure,
            "battery_voltage": sensor_reading.battery_voltage,
            "transmission_temp": sensor_reading.transmission_temp,
            "mileage": sensor_reading.mileage,
            "dtc_codes": sensor_reading.dtc_codes,
            "timestamp": sensor_reading.timestamp.isoformat() if sensor_reading.timestamp else None
        }
    
    async def _get_sensor_data_at_time(
        self,
        db: AsyncSession,
        vehicle_id: int,
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get sensor reading closest to given timestamp"""
        query = select(SensorReading).where(
            SensorReading.vehicle_id == vehicle_id,
            SensorReading.timestamp <= timestamp
        ).order_by(SensorReading.timestamp.desc()).limit(1)
        
        result = await db.execute(query)
        sensor_reading = result.scalar_one_or_none()
        
        if not sensor_reading:
            return None
        
        return {
            "rpm": sensor_reading.rpm,
            "speed": sensor_reading.speed,
            "coolant_temp": sensor_reading.coolant_temp,
            "battery_voltage": sensor_reading.battery_voltage,
            "mileage": sensor_reading.mileage,
            "timestamp": sensor_reading.timestamp.isoformat()
        }


def get_diagnosis_service() -> DiagnosisService:
    """Get diagnosis service instance"""
    return DiagnosisService()
