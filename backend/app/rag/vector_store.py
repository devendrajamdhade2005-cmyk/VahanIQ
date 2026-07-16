"""
FAISS vector store for semantic search
"""

import os
import pickle
import logging
from typing import List, Tuple, Optional, Dict, Any

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️  RAG libraries not available. Using mock vector store.")

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    FAISS-based vector store for semantic search
    Supports adding documents, searching, and persistence
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize vector store"""
        if self._initialized:
            return
            
        self.model_name = settings.RAG_EMBEDDINGS_MODEL
        self.index_path = settings.RAG_INDEX_PATH
        self.embedding_model: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.metadata: List[Dict[str, Any]] = []
        self.dimension: Optional[int] = None
        
        self._initialized = True
        logger.info(f"VectorStore initialized with model: {self.model_name}")
    
    def initialize(self):
        """Load or create embedding model and FAISS index"""
        if not RAG_AVAILABLE:
            logger.warning("RAG libraries not available. Using mock vector store.")
            self.embedding_model = None
            self.index = None
            self.dimension = 384  # Mock dimension
            return
            
        try:
            # Load sentence transformer model
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            self.dimension = self.embedding_model.get_sentence_embedding_dimension()
            logger.info(f"Embedding dimension: {self.dimension}")
            
            # Try to load existing index
            if os.path.exists(f"{self.index_path}.faiss"):
                self.load()
            else:
                # Create new index
                logger.info("Creating new FAISS index")
                self.index = faiss.IndexFlatL2(self.dimension)
                self.metadata = []
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            logger.info(f"VectorStore ready with {self.index.ntotal} documents")
            
        except Exception as e:
            logger.error(f"Failed to initialize VectorStore: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not initialized. Call initialize() first.")
        
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        return embedding.astype('float32')
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Matrix of embeddings (n_texts x dimension)
        """
        if self.embedding_model is None:
            raise RuntimeError("Embedding model not initialized. Call initialize() first.")
        
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return embeddings.astype('float32')
    
    def add_documents(
        self,
        texts: List[str],
        metadata_list: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Add documents to the vector store
        
        Args:
            texts: List of document texts
            metadata_list: List of metadata dicts for each document
            
        Returns:
            List of document IDs (indices)
        """
        if self.index is None:
            raise RuntimeError("Index not initialized. Call initialize() first.")
        
        if len(texts) != len(metadata_list):
            raise ValueError("Number of texts and metadata must match")
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents")
        embeddings = self.embed_texts(texts)
        
        # Add to index
        start_id = self.index.ntotal
        self.index.add(embeddings)
        
        # Store metadata
        self.metadata.extend(metadata_list)
        
        doc_ids = list(range(start_id, self.index.ntotal))
        logger.info(f"Added {len(texts)} documents (IDs: {start_id} to {self.index.ntotal - 1})")
        
        return doc_ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Semantic search for similar documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters (e.g., {"doc_type": "manual"})
            
        Returns:
            List of (metadata, distance) tuples, sorted by relevance
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        # Generate query embedding
        query_embedding = self.embed_text(query)
        query_embedding = np.expand_dims(query_embedding, axis=0)
        
        # Search
        # If we have filters, we might need to search more and filter
        search_k = top_k * 3 if filters else top_k
        distances, indices = self.index.search(query_embedding, min(search_k, self.index.ntotal))
        
        # Collect results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            meta = self.metadata[idx].copy()
            
            # Apply filters if provided
            if filters:
                match = all(meta.get(k) == v for k, v in filters.items())
                if not match:
                    continue
            
            # Convert L2 distance to similarity score (0-1, higher is better)
            similarity = 1 / (1 + float(dist))
            results.append((meta, similarity))
            
            if len(results) >= top_k:
                break
        
        logger.info(f"Search for '{query[:50]}...' returned {len(results)} results")
        return results
    
    def search_by_embedding(
        self,
        embedding: np.ndarray,
        top_k: int = 5
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Search using pre-computed embedding
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (metadata, similarity) tuples
        """
        if self.index is None or self.index.ntotal == 0:
            return []
        
        embedding = np.expand_dims(embedding.astype('float32'), axis=0)
        distances, indices = self.index.search(embedding, min(top_k, self.index.ntotal))
        
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            
            similarity = 1 / (1 + float(dist))
            results.append((self.metadata[idx].copy(), similarity))
        
        return results
    
    def save(self):
        """Persist index and metadata to disk"""
        if self.index is None:
            raise RuntimeError("Cannot save uninitialized index")
        
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            
            # Save FAISS index
            faiss.write_index(self.index, f"{self.index_path}.faiss")
            
            # Save metadata
            with open(f"{self.index_path}.metadata", 'wb') as f:
                pickle.dump(self.metadata, f)
            
            logger.info(f"Saved vector store with {self.index.ntotal} documents to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
            raise
    
    def load(self):
        """Load index and metadata from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Load metadata
            with open(f"{self.index_path}.metadata", 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"Loaded vector store with {self.index.ntotal} documents from {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to load vector store: {e}")
            raise
    
    def clear(self):
        """Clear all documents from the index"""
        if self.dimension is None:
            raise RuntimeError("Dimension not set. Call initialize() first.")
        
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info("Cleared vector store")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        return {
            "total_documents": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "model": self.model_name,
            "index_path": self.index_path,
            "metadata_count": len(self.metadata)
        }
