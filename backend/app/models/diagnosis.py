"""
Diagnosis model - AI-generated failure predictions
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class FailureType(str, enum.Enum):
    """Types of vehicle failures"""
    ENGINE = "engine"
    TRANSMISSION = "transmission"
    BRAKE = "brake"
    ELECTRICAL = "electrical"
    SUSPENSION = "suspension"
    COOLING = "cooling"
    FUEL_SYSTEM = "fuel_system"
    EXHAUST = "exhaust"
    OTHER = "other"


class DiagnosisStatus(str, enum.Enum):
    """Diagnosis lifecycle status"""
    PREDICTED = "predicted"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class Diagnosis(Base):
    """AI-generated diagnosis model"""
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    
    # Prediction details
    failure_type = Column(SQLEnum(FailureType), nullable=False, index=True)
    failure_probability = Column(Float, nullable=False)  # 0.0 to 1.0
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # AI explanation
    explanation_text = Column(Text, nullable=False)  # Plain-language explanation
    technical_details = Column(Text, nullable=True)  # Technical details for mechanics
    shap_values = Column(Text, nullable=True)  # JSON string of SHAP values
    
    # Contributing factors
    primary_sensor_signals = Column(Text, nullable=True)  # JSON list of key sensor readings
    
    # Recommendations
    recommended_actions = Column(Text, nullable=True)  # JSON list of recommended actions
    estimated_time_to_failure = Column(Float, nullable=True)  # Days/hours estimate
    
    # Status tracking
    status = Column(SQLEnum(DiagnosisStatus), default=DiagnosisStatus.PREDICTED, nullable=False, index=True)
    is_critical = Column(Boolean, default=False, nullable=False, index=True)
    
    # ML model info
    model_version = Column(String(50), nullable=True)
    prediction_confidence = Column(Float, nullable=True)  # Model confidence score
    
    # Timestamps
    predicted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="diagnoses")
    repair_cases = relationship("RepairCase", back_populates="diagnosis")
    
    def __repr__(self):
        return f"<Diagnosis(id={self.id}, vehicle_id={self.vehicle_id}, type={self.failure_type}, prob={self.failure_probability:.2f})>"
