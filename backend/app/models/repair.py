"""
Repair case and repair steps models
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class RepairStatus(str, enum.Enum):
    """Repair case status"""
    WAITING = "waiting"
    DIAGNOSING = "diagnosing"
    IN_REPAIR = "in_repair"
    QC = "qc"  # Quality Check
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FeedbackOutcome(str, enum.Enum):
    """Mechanic feedback on diagnosis accuracy"""
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"


class RepairCase(Base):
    """Repair case model - tracks the entire repair journey"""
    __tablename__ = "repair_cases"

    id = Column(Integer, primary_key=True, index=True)
    
    # References
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=True, index=True)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    showroom_id = Column(Integer, ForeignKey("showrooms.id"), nullable=False, index=True)
    
    # Case details
    case_number = Column(String(50), unique=True, nullable=False, index=True)  # e.g., RC-2024-001234
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Status
    status = Column(SQLEnum(RepairStatus), default=RepairStatus.WAITING, nullable=False, index=True)
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    
    # Time tracking
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    estimated_completion = Column(DateTime(timezone=True), nullable=True)
    actual_duration_minutes = Column(Integer, nullable=True)
    
    # Cost
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)
    labor_cost = Column(Float, nullable=True)
    parts_cost = Column(Float, nullable=True)
    
    # Customer approval
    requires_approval = Column(Boolean, default=True, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Mechanic feedback (for continuous learning)
    mechanic_feedback = Column(Text, nullable=True)
    diagnosis_accuracy = Column(SQLEnum(FeedbackOutcome), nullable=True)
    actual_issue_found = Column(Text, nullable=True)
    
    # Internal notes
    internal_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="repair_cases")
    diagnosis = relationship("Diagnosis", back_populates="repair_cases")
    technician = relationship("User", back_populates="assigned_repairs", foreign_keys=[technician_id])
    showroom = relationship("Showroom", back_populates="repair_cases")
    repair_steps = relationship("RepairStep", back_populates="repair_case", cascade="all, delete-orphan")
    parts_used = relationship("PartUsage", back_populates="repair_case", cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="repair_case", uselist=False)
    
    def __repr__(self):
        return f"<RepairCase(id={self.id}, case_number={self.case_number}, status={self.status})>"


class RepairStep(Base):
    """Individual repair steps - checklist for mechanic"""
    __tablename__ = "repair_steps"

    id = Column(Integer, primary_key=True, index=True)
    repair_case_id = Column(Integer, ForeignKey("repair_cases.id"), nullable=False, index=True)
    
    # Step details
    step_number = Column(Integer, nullable=False)  # Order in sequence
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    is_safety_critical = Column(Boolean, default=False, nullable=False)
    
    # Completion tracking
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Time estimate
    estimated_duration_minutes = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    repair_case = relationship("RepairCase", back_populates="repair_steps")
    
    def __repr__(self):
        return f"<RepairStep(id={self.id}, step={self.step_number}, completed={self.is_completed})>"
