"""
Pydantic schemas for knowledge base
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class KnowledgeDocumentBase(BaseModel):
    """Base knowledge document schema"""
    title: str = Field(..., min_length=1, max_length=500)
    doc_type: str = Field(..., description="Type: manual, bulletin, guide, faq")
    category: Optional[str] = Field(None, max_length=100, description="e.g., 'Brake System', 'Engine'")
    content: str = Field(..., min_length=1)
    content_summary: Optional[str] = None
    file_url: Optional[str] = Field(None, max_length=500)
    file_type: Optional[str] = Field(None, max_length=20)
    applicable_makes: Optional[str] = Field(None, description="Comma-separated vehicle makes")
    applicable_models: Optional[str] = Field(None, description="Comma-separated vehicle models")
    year_from: Optional[int] = Field(None, ge=1900, le=2100)
    year_to: Optional[int] = Field(None, ge=1900, le=2100)
    is_active: bool = True
    is_verified: bool = False
    version: Optional[str] = Field(None, max_length=20)


class KnowledgeDocumentCreate(KnowledgeDocumentBase):
    """Schema for creating knowledge document"""
    pass


class KnowledgeDocumentUpdate(BaseModel):
    """Schema for updating knowledge document"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    doc_type: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    content_summary: Optional[str] = None
    file_url: Optional[str] = None
    applicable_makes: Optional[str] = None
    applicable_models: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    version: Optional[str] = None


class KnowledgeDocumentResponse(KnowledgeDocumentBase):
    """Schema for knowledge document response"""
    id: int
    embedding_id: Optional[str] = None
    chunk_index: Optional[int] = None
    superseded_by: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class KnowledgeSearchRequest(BaseModel):
    """Schema for knowledge search request"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    doc_type: Optional[str] = None
    category: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None


class KnowledgeSearchResult(BaseModel):
    """Schema for search result"""
    content: str
    title: str
    doc_type: str
    category: Optional[str] = None
    similarity: float
    doc_id: int
    chunk_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeSearchResponse(BaseModel):
    """Schema for search response"""
    query: str
    results: List[KnowledgeSearchResult]
    total_results: int
    search_time_ms: float


class SimilarCaseRequest(BaseModel):
    """Schema for similar case search"""
    diagnosis_text: str = Field(..., min_length=1)
    failure_type: str = Field(..., description="brake, engine, fuel, electrical, etc.")
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class SimilarCaseResult(BaseModel):
    """Schema for similar case result"""
    repair_case_id: int
    failure_type: str
    description: str
    resolution_notes: Optional[str] = None
    cost: Optional[float] = None
    duration_hours: Optional[float] = None
    similarity: float
    case_text: str


class SimilarCaseResponse(BaseModel):
    """Schema for similar case response"""
    results: List[SimilarCaseResult]
    total_results: int


class RepairContextRequest(BaseModel):
    """Schema for repair context request"""
    failure_type: str
    diagnosis_description: str
    vehicle_make: str
    vehicle_model: str
    dtc_codes: Optional[List[str]] = Field(default_factory=list)


class RepairContextResponse(BaseModel):
    """Schema for repair context response"""
    query: str
    knowledge_articles: List[KnowledgeSearchResult]
    similar_cases: List[SimilarCaseResult]
    vehicle: Dict[str, str]
    failure_type: str
    retrieved_at: str


class IndexStatsResponse(BaseModel):
    """Schema for index statistics"""
    total_documents: int
    dimension: Optional[int] = None
    model: str
    index_path: str
    metadata_count: int
    status: Optional[str] = None


class IndexRebuildRequest(BaseModel):
    """Schema for index rebuild request"""
    rebuild: bool = Field(default=True, description="Whether to rebuild from scratch")


class IndexRebuildResponse(BaseModel):
    """Schema for index rebuild response"""
    indexed: int
    total: int
    chunks: int
    timestamp: str
