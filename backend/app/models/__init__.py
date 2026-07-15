"""
Database models for AutoSense AI Platform

All SQLAlchemy models must be imported here so that Base.metadata.create_all()
can discover and create all tables.
"""

from app.models.user import User, UserRole
from app.models.showroom import Showroom
from app.models.vehicle import Vehicle, VehicleStatus
from app.models.sensor import SensorReading
from app.models.diagnosis import Diagnosis, FailureType, DiagnosisStatus
from app.models.repair import RepairCase, RepairStep, RepairStatus, FeedbackOutcome
from app.models.part import Part, PartUsage
from app.models.appointment import Appointment, AppointmentStatus
from app.models.invoice import Invoice
from app.models.knowledge import KnowledgeDocument
from app.models.audit import AuditLog

__all__ = [
    # User & Auth
    "User",
    "UserRole",
    
    # Core entities
    "Showroom",
    "Vehicle",
    "VehicleStatus",
    
    # Sensor data
    "SensorReading",
    
    # AI Diagnosis
    "Diagnosis",
    "FailureType",
    "DiagnosisStatus",
    
    # Repair workflow
    "RepairCase",
    "RepairStep",
    "RepairStatus",
    "FeedbackOutcome",
    
    # Parts inventory
    "Part",
    "PartUsage",
    
    # Appointments
    "Appointment",
    "AppointmentStatus",
    
    # Billing
    "Invoice",
    
    # Knowledge base
    "KnowledgeDocument",
    
    # Audit
    "AuditLog",
]
