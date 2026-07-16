"""
Knowledge base and RAG API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import time

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.knowledge import KnowledgeDocument
from app.schemas.knowledge import (
    KnowledgeDocumentCreate,
    KnowledgeDocumentUpdate,
    KnowledgeDocumentResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    SimilarCaseRequest,
    SimilarCaseResponse,
    SimilarCaseResult,
    RepairContextRequest,
    RepairContextResponse,
    IndexStatsResponse,
    IndexRebuildRequest,
    IndexRebuildResponse
)
from app.rag.retrieval_service import get_retrieval_service
from sqlalchemy import select, and_

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(
    request: KnowledgeSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Search knowledge base semantically
    
    Returns relevant document chunks based on query
    """
    start_time = time.time()
    
    retrieval_service = get_retrieval_service()
    
    try:
        results = await retrieval_service.search_knowledge(
            query=request.query,
            top_k=request.top_k,
            doc_type=request.doc_type,
            category=request.category,
            vehicle_make=request.vehicle_make,
            vehicle_model=request.vehicle_model
        )
        
        search_time_ms = (time.time() - start_time) * 1000
        
        return KnowledgeSearchResponse(
            query=request.query,
            results=[KnowledgeSearchResult(**r) for r in results],
            total_results=len(results),
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/similar-cases", response_model=SimilarCaseResponse)
async def find_similar_cases(
    request: SimilarCaseRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Find similar repair cases based on diagnosis
    
    Returns past repair cases with similar symptoms and failures
    """
    retrieval_service = get_retrieval_service()
    
    try:
        results = await retrieval_service.find_similar_cases(
            db=db,
            diagnosis_text=request.diagnosis_text,
            failure_type=request.failure_type,
            vehicle_make=request.vehicle_make,
            vehicle_model=request.vehicle_model,
            top_k=request.top_k
        )
        
        return SimilarCaseResponse(
            results=[SimilarCaseResult(**r) for r in results],
            total_results=len(results)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Similar case search failed: {str(e)}"
        )


@router.post("/repair-context", response_model=RepairContextResponse)
async def get_repair_context(
    request: RepairContextRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive repair context
    
    Combines knowledge base articles and similar cases for repair guidance
    """
    retrieval_service = get_retrieval_service()
    
    try:
        context = await retrieval_service.get_repair_context(
            db=db,
            failure_type=request.failure_type,
            diagnosis_description=request.diagnosis_description,
            vehicle_make=request.vehicle_make,
            vehicle_model=request.vehicle_model,
            dtc_codes=request.dtc_codes
        )
        
        return RepairContextResponse(
            query=context["query"],
            knowledge_articles=[KnowledgeSearchResult(**r) for r in context["knowledge_articles"]],
            similar_cases=[SimilarCaseResult(**r) for r in context["similar_cases"]],
            vehicle=context["vehicle"],
            failure_type=context["failure_type"],
            retrieved_at=context["retrieved_at"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get repair context: {str(e)}"
        )


@router.get("/stats", response_model=IndexStatsResponse)
async def get_index_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get vector store statistics
    
    Returns information about indexed documents and vector store status
    """
    retrieval_service = get_retrieval_service()
    
    try:
        stats = retrieval_service.get_vector_store_stats()
        return IndexStatsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.post("/index/rebuild", response_model=IndexRebuildResponse)
async def rebuild_index(
    request: IndexRebuildRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Rebuild vector index from knowledge base
    
    Admin only - Re-indexes all knowledge documents into vector store
    """
    retrieval_service = get_retrieval_service()
    
    try:
        stats = await retrieval_service.index_knowledge_base(
            db=db,
            rebuild=request.rebuild
        )
        
        return IndexRebuildResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Index rebuild failed: {str(e)}"
        )


@router.get("/documents", response_model=List[KnowledgeDocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    doc_type: str | None = None,
    category: str | None = None,
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List knowledge documents
    
    Returns paginated list of knowledge base documents with filters
    """
    query = select(KnowledgeDocument)
    
    # Apply filters
    filters = [KnowledgeDocument.is_active == is_active]
    if doc_type:
        filters.append(KnowledgeDocument.doc_type == doc_type)
    if category:
        filters.append(KnowledgeDocument.category == category)
    
    query = query.where(and_(*filters)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return documents


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get knowledge document by ID
    
    Returns full document details including content
    """
    query = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge document not found"
        )
    
    return document


@router.post("/documents", response_model=KnowledgeDocumentResponse)
async def create_document(
    document: KnowledgeDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create knowledge document
    
    Admin only - Add new document to knowledge base
    """
    db_document = KnowledgeDocument(**document.model_dump())
    
    db.add(db_document)
    await db.commit()
    await db.refresh(db_document)
    
    return db_document


@router.put("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def update_document(
    document_id: int,
    document: KnowledgeDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update knowledge document
    
    Admin only - Update existing document
    """
    query = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    result = await db.execute(query)
    db_document = result.scalar_one_or_none()
    
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge document not found"
        )
    
    # Update fields
    update_data = document.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    await db.commit()
    await db.refresh(db_document)
    
    return db_document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete knowledge document
    
    Admin only - Soft delete document (sets is_active to False)
    """
    query = select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
    result = await db.execute(query)
    db_document = result.scalar_one_or_none()
    
    if not db_document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge document not found"
        )
    
    db_document.is_active = False
    await db.commit()
    
    return None
