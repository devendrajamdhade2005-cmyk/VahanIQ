"""
Retrieval service for RAG pipeline
Provides high-level interface for semantic search and similar case retrieval
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.rag.vector_store import VectorStore
from app.rag.document_processor import DocumentProcessor
from app.models.knowledge import KnowledgeDocument
from app.models.diagnosis import Diagnosis
from app.models.repair import RepairCase
from app.models.vehicle import Vehicle
from app.core.config import settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    High-level service for retrieving relevant information
    Combines vector search with database queries
    """
    
    def __init__(self):
        """Initialize retrieval service"""
        self.vector_store = VectorStore()
        self.doc_processor = DocumentProcessor(
            chunk_size=500,
            chunk_overlap=50
        )
        self.initialized = False
    
    async def initialize(self):
        """Initialize vector store and load documents"""
        if not self.initialized:
            self.vector_store.initialize()
            self.initialized = True
            logger.info("RetrievalService initialized")
    
    async def index_knowledge_base(
        self,
        db: AsyncSession,
        rebuild: bool = False
    ) -> Dict[str, Any]:
        """
        Index all knowledge base documents into vector store
        
        Args:
            db: Database session
            rebuild: Whether to rebuild index from scratch
            
        Returns:
            Statistics about indexing
        """
        await self.initialize()
        
        if rebuild:
            self.vector_store.clear()
            logger.info("Rebuilding vector store from scratch")
        
        # Fetch active documents
        query = select(KnowledgeDocument).where(
            and_(
                KnowledgeDocument.is_active == True,
                KnowledgeDocument.content.isnot(None)
            )
        )
        result = await db.execute(query)
        documents = result.scalars().all()
        
        if not documents:
            logger.warning("No knowledge documents found to index")
            return {"indexed": 0, "total": 0}
        
        # Process documents into chunks
        doc_dicts = [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "doc_type": doc.doc_type,
                "category": doc.category,
                "applicable_makes": doc.applicable_makes,
                "applicable_models": doc.applicable_models,
                "year_from": doc.year_from,
                "year_to": doc.year_to
            }
            for doc in documents
        ]
        
        chunks = self.doc_processor.batch_process_documents(doc_dicts)
        
        # Extract texts and metadata
        texts = [chunk_text for chunk_text, _ in chunks]
        metadata_list = [metadata for _, metadata in chunks]
        
        # Add to vector store
        doc_ids = self.vector_store.add_documents(texts, metadata_list)
        
        # Save index
        self.vector_store.save()
        
        stats = {
            "indexed": len(doc_ids),
            "total": len(documents),
            "chunks": len(chunks),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Indexed {stats['indexed']} documents into {stats['chunks']} chunks")
        return stats
    
    async def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        doc_type: Optional[str] = None,
        category: Optional[str] = None,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base semantically
        
        Args:
            query: Search query
            top_k: Number of results to return
            doc_type: Filter by document type
            category: Filter by category
            vehicle_make: Filter by vehicle make
            vehicle_model: Filter by vehicle model
            
        Returns:
            List of relevant document chunks with metadata
        """
        await self.initialize()
        
        # Build filters
        filters = {}
        if doc_type:
            filters["doc_type"] = doc_type
        if category:
            filters["category"] = category
        
        # Search vector store
        results = self.vector_store.search(
            query=query,
            top_k=top_k * 2,  # Get more for additional filtering
            filters=filters if filters else None
        )
        
        # Post-filter by vehicle applicability
        filtered_results = []
        for metadata, similarity in results:
            # Check vehicle make/model applicability
            if vehicle_make:
                applicable_makes = metadata.get("applicable_makes", "")
                if applicable_makes and vehicle_make not in applicable_makes.split(","):
                    continue
            
            if vehicle_model:
                applicable_models = metadata.get("applicable_models", "")
                if applicable_models and vehicle_model not in applicable_models.split(","):
                    continue
            
            filtered_results.append({
                "content": metadata.get("content", ""),
                "title": metadata.get("title", ""),
                "doc_type": metadata.get("doc_type", ""),
                "category": metadata.get("category", ""),
                "similarity": similarity,
                "doc_id": metadata.get("doc_id"),
                "chunk_index": metadata.get("chunk_index", 0),
                "metadata": metadata
            })
            
            if len(filtered_results) >= top_k:
                break
        
        logger.info(f"Knowledge search for '{query[:50]}...' returned {len(filtered_results)} results")
        return filtered_results
    
    async def find_similar_cases(
        self,
        db: AsyncSession,
        diagnosis_text: str,
        failure_type: str,
        vehicle_make: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar repair cases based on diagnosis
        
        Args:
            db: Database session
            diagnosis_text: Current diagnosis description
            failure_type: Type of failure
            vehicle_make: Vehicle make for filtering
            vehicle_model: Vehicle model for filtering
            top_k: Number of similar cases to return
            
        Returns:
            List of similar repair cases with details
        """
        await self.initialize()
        
        # Build search query combining diagnosis and failure type
        search_query = f"{failure_type} failure: {diagnosis_text}"
        
        # Query database for completed repair cases
        query = select(RepairCase).join(
            Diagnosis, RepairCase.diagnosis_id == Diagnosis.id
        ).join(
            Vehicle, Diagnosis.vehicle_id == Vehicle.id
        ).where(
            RepairCase.status == "completed"
        )
        
        # Filter by vehicle if provided
        if vehicle_make:
            query = query.where(Vehicle.make.ilike(f"%{vehicle_make}%"))
        if vehicle_model:
            query = query.where(Vehicle.model.ilike(f"%{vehicle_model}%"))
        
        result = await db.execute(query)
        repair_cases = result.scalars().all()
        
        if not repair_cases:
            logger.info("No similar cases found in database")
            return []
        
        # Create embeddings for search
        case_texts = []
        case_metadata = []
        
        for case in repair_cases:
            # Combine relevant text from repair case
            case_text = f"{case.failure_type} - {case.description}"
            if case.resolution_notes:
                case_text += f" Resolution: {case.resolution_notes}"
            
            case_texts.append(case_text)
            case_metadata.append({
                "repair_case_id": case.id,
                "failure_type": case.failure_type,
                "description": case.description,
                "resolution_notes": case.resolution_notes,
                "cost": case.total_cost,
                "duration_hours": case.actual_hours,
                "created_at": case.created_at.isoformat() if case.created_at else None
            })
        
        # Generate embeddings for repair cases
        case_embeddings = self.vector_store.embed_texts(case_texts)
        
        # Generate embedding for query
        query_embedding = self.vector_store.embed_text(search_query)
        
        # Calculate similarities
        import numpy as np
        
        # Cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        case_norms = case_embeddings / np.linalg.norm(case_embeddings, axis=1, keepdims=True)
        similarities = np.dot(case_norms, query_norm)
        
        # Sort by similarity
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Build results
        similar_cases = []
        for idx in top_indices:
            idx = int(idx)
            metadata = case_metadata[idx].copy()
            metadata["similarity"] = float(similarities[idx])
            metadata["case_text"] = case_texts[idx]
            similar_cases.append(metadata)
        
        logger.info(f"Found {len(similar_cases)} similar cases for '{failure_type}'")
        return similar_cases
    
    async def get_repair_context(
        self,
        db: AsyncSession,
        failure_type: str,
        diagnosis_description: str,
        vehicle_make: str,
        vehicle_model: str,
        dtc_codes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive repair context combining knowledge base and similar cases
        
        Args:
            db: Database session
            failure_type: Type of failure
            diagnosis_description: Diagnosis description
            vehicle_make: Vehicle make
            vehicle_model: Vehicle model
            dtc_codes: Optional DTC codes
            
        Returns:
            Combined context with knowledge articles and similar cases
        """
        await self.initialize()
        
        # Build search query
        search_terms = [failure_type, diagnosis_description]
        if dtc_codes:
            search_terms.extend(dtc_codes)
        search_query = " ".join(search_terms)
        
        # Search knowledge base
        knowledge_results = await self.search_knowledge(
            query=search_query,
            top_k=settings.RAG_TOP_K_RESULTS,
            category=failure_type,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model
        )
        
        # Find similar cases
        similar_cases = await self.find_similar_cases(
            db=db,
            diagnosis_text=diagnosis_description,
            failure_type=failure_type,
            vehicle_make=vehicle_make,
            vehicle_model=vehicle_model,
            top_k=3
        )
        
        context = {
            "query": search_query,
            "knowledge_articles": knowledge_results,
            "similar_cases": similar_cases,
            "vehicle": {
                "make": vehicle_make,
                "model": vehicle_model
            },
            "failure_type": failure_type,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
        logger.info(
            f"Retrieved repair context: {len(knowledge_results)} articles, "
            f"{len(similar_cases)} similar cases"
        )
        
        return context
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if not self.initialized:
            return {"status": "not_initialized"}
        
        return self.vector_store.get_stats()


# Singleton instance
_retrieval_service: Optional[RetrievalService] = None


def get_retrieval_service() -> RetrievalService:
    """Get singleton retrieval service instance"""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service
