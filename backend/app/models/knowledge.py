"""
Knowledge base model for RAG system
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class KnowledgeDocument(Base):
    """Knowledge base documents for RAG system"""
    __tablename__ = "knowledge_docs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Document details
    title = Column(String(500), nullable=False, index=True)
    doc_type = Column(String(50), nullable=False, index=True)  # manual, bulletin, guide, faq
    category = Column(String(100), nullable=True)  # e.g., "Brake System", "Engine"
    
    # Content
    content = Column(Text, nullable=False)
    content_summary = Column(Text, nullable=True)
    
    # File reference
    file_url = Column(String(500), nullable=True)  # Original file location (S3/storage)
    file_type = Column(String(20), nullable=True)  # pdf, txt, html
    
    # RAG metadata
    embedding_id = Column(String(100), nullable=True, index=True)  # Reference to FAISS index
    chunk_index = Column(Integer, nullable=True)  # If document is split into chunks
    
    # Vehicle applicability
    applicable_makes = Column(String(500), nullable=True)  # Comma-separated: "Tata,Mahindra"
    applicable_models = Column(String(500), nullable=True)  # Comma-separated
    year_from = Column(Integer, nullable=True)
    year_to = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Version control
    version = Column(String(20), nullable=True)
    superseded_by = Column(Integer, nullable=True)  # ID of newer version
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<KnowledgeDocument(id={self.id}, title={self.title[:50]}, type={self.doc_type})>"
