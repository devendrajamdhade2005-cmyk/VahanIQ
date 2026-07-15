"""
Pydantic schemas for diagnosis
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DiagnosisCreate(BaseModel):
    """Schema for creating diagnosis"""
    vehicle_id: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=2000, description="Mechanic's observations")
    generate_repair_guide: bool = Field(default=True, description="Generate AI repair guide")


class DiagnosisUpdate(BaseModel):
    """Schema for updating diagnosis"""
    description: Optional[str] = Field(None, max_length=2000)
    recommended_actions: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|in_progress|completed|cancelled)$")
    mechanic_feedback: Optional[str] = None
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5)


class RepairStep(BaseModel):
    """Schema for repair step"""
    step_number: int
    title: str
    description: str
    safety_warning: Optional[str] = None
    estimated_time_minutes: int


class RequiredPart(BaseModel):
    """Schema for required part"""
    part_name: str
    part_number: Optional[str] = None
    quantity: int = 1
    estimated_cost_inr: float
    priority: str = Field(..., pattern="^(critical|recommended|optional)$")


class RepairGuide(BaseModel):
    """Schema for AI-generated repair guide"""
    diagnosis_summary: str
    root_cause: str
    urgency: str = Field(..., pattern="^(immediate|urgent|moderate|low)$")
    repair_steps: List[RepairStep]
    required_parts: List[RequiredPart]
    required_tools: List[str]
    estimated_labor_hours: float
    estimated_total_cost_inr: float
    safety_precautions: List[str]
    quality_checks: List[str]
    common_mistakes: List[str]
    additional_notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MLPrediction(BaseModel):
    """Schema for ML prediction results"""
    failure_type: str
    probability: float = Field(..., ge=0, le=1)
    severity: str
    explanation: str
    top_features: Optional[List[Dict[str, Any]]] = None


class KnowledgeArticleSummary(BaseModel):
    """Schema for knowledge article summary"""
    title: str
    doc_type: str
    category: Optional[str] = None
    similarity: float
    content: str = Field(..., description="Relevant content excerpt")


class SimilarCaseSummary(BaseModel):
    """Schema for similar case summary"""
    repair_case_id: int
    failure_type: str
    description: str
    resolution_notes: Optional[str] = None
    cost: Optional[float] = None
    duration_hours: Optional[float] = None
    similarity: float


class RAGContextSummary(BaseModel):
    """Schema for RAG context summary"""
    knowledge_articles_count: int
    similar_cases_count: int
    knowledge_articles: List[KnowledgeArticleSummary]
    similar_cases: List[SimilarCaseSummary]


class VehicleSummary(BaseModel):
    """Schema for vehicle summary in diagnosis"""
    id: int
    make: str
    model: str
    year: int
    registration_number: str
    mileage: float
    health_status: str


class DiagnosisSummary(BaseModel):
    """Schema for diagnosis summary"""
    id: int
    vehicle_id: int
    failure_type: str
    confidence_score: float
    severity: str
    status: str
    created_at: str


class CompleteDiagnosisResponse(BaseModel):
    """Schema for complete diagnosis response"""
    diagnosis: DiagnosisSummary
    vehicle: VehicleSummary
    ml_prediction: MLPrediction
    rag_context: RAGContextSummary
    repair_guide: Optional[RepairGuide] = None
    customer_summary: Optional[str] = Field(None, description="Plain-language summary for customer")
    sensor_data_timestamp: Optional[str] = None


class DiagnosisDetailResponse(BaseModel):
    """Schema for detailed diagnosis response"""
    diagnosis: Dict[str, Any]
    vehicle: Dict[str, Any]
    sensor_data: Optional[Dict[str, Any]] = None
    rag_context: Optional[Dict[str, Any]] = None


class RegenerateGuideRequest(BaseModel):
    """Schema for regenerating repair guide"""
    custom_notes: Optional[str] = Field(None, max_length=2000, description="Additional notes to incorporate")


class DiagnosisListResponse(BaseModel):
    """Schema for diagnosis list item"""
    id: int
    vehicle_id: int
    vehicle_info: str = Field(..., description="Vehicle make/model/year")
    failure_type: str
    confidence_score: float
    severity: str
    status: str
    estimated_repair_cost: Optional[float] = None
    estimated_repair_hours: Optional[float] = None
    created_at: str
    mechanic_name: str


class DiagnosisStatsResponse(BaseModel):
    """Schema for diagnosis statistics"""
    total_diagnoses: int
    by_failure_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    average_confidence: float
    accuracy_stats: Optional[Dict[str, Any]] = None
