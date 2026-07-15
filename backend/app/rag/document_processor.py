"""
Document processing for RAG pipeline
Handles chunking, cleaning, and metadata extraction
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Process documents for RAG ingestion
    Handles text chunking, cleaning, and metadata preparation
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        min_chunk_size: int = 50
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Target size of text chunks (in words)
            chunk_overlap: Number of overlapping words between chunks
            min_chunk_size: Minimum chunk size to keep
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        # Strip
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str, preserve_sentences: bool = True) -> List[str]:
        """
        Split text into chunks with overlap
        
        Args:
            text: Text to chunk
            preserve_sentences: Try to keep sentences intact
            
        Returns:
            List of text chunks
        """
        # Clean text first
        text = self.clean_text(text)
        
        if preserve_sentences:
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
        else:
            # Split into words
            words = text.split()
            sentences = [' '.join(words[i:i+self.chunk_size]) 
                        for i in range(0, len(words), self.chunk_size)]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence exceeds chunk size, save current chunk
            if current_size + sentence_words > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text.split()) >= self.min_chunk_size:
                    chunks.append(chunk_text)
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    # Keep last N words for overlap
                    overlap_text = ' '.join(current_chunk)
                    overlap_words = overlap_text.split()[-self.chunk_overlap:]
                    current_chunk = overlap_words
                    current_size = len(overlap_words)
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_words
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.split()) >= self.min_chunk_size:
                chunks.append(chunk_text)
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def extract_metadata(
        self,
        text: str,
        doc_id: int,
        title: str,
        doc_type: str,
        **extra_metadata
    ) -> Dict[str, Any]:
        """
        Extract metadata for a document chunk
        
        Args:
            text: Chunk text
            doc_id: Document ID from database
            title: Document title
            doc_type: Document type
            **extra_metadata: Additional metadata fields
            
        Returns:
            Metadata dictionary
        """
        # Generate content hash for deduplication
        content_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        
        metadata = {
            "doc_id": doc_id,
            "title": title,
            "doc_type": doc_type,
            "content": text,
            "content_hash": content_hash,
            "word_count": len(text.split()),
            "char_count": len(text),
            "indexed_at": datetime.utcnow().isoformat(),
        }
        
        # Add extra metadata
        metadata.update(extra_metadata)
        
        return metadata
    
    def process_document(
        self,
        doc_id: int,
        title: str,
        content: str,
        doc_type: str,
        category: Optional[str] = None,
        applicable_makes: Optional[str] = None,
        applicable_models: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        **extra_fields
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Process a complete document into chunks with metadata
        
        Args:
            doc_id: Database document ID
            title: Document title
            content: Full document content
            doc_type: Type of document
            category: Document category
            applicable_makes: Comma-separated vehicle makes
            applicable_models: Comma-separated vehicle models
            year_from: Applicable from year
            year_to: Applicable to year
            **extra_fields: Additional metadata fields
            
        Returns:
            List of (chunk_text, metadata) tuples
        """
        # Chunk the content
        chunks = self.chunk_text(content)
        
        # Prepare base metadata
        base_metadata = {
            "doc_type": doc_type,
            "category": category,
            "applicable_makes": applicable_makes,
            "applicable_models": applicable_models,
            "year_from": year_from,
            "year_to": year_to,
        }
        base_metadata.update(extra_fields)
        
        # Create chunk metadata
        processed_chunks = []
        for chunk_idx, chunk_text in enumerate(chunks):
            metadata = self.extract_metadata(
                text=chunk_text,
                doc_id=doc_id,
                title=f"{title} (Part {chunk_idx + 1}/{len(chunks)})",
                chunk_index=chunk_idx,
                total_chunks=len(chunks),
                **base_metadata
            )
            processed_chunks.append((chunk_text, metadata))
        
        logger.info(f"Processed document '{title}' into {len(processed_chunks)} chunks")
        return processed_chunks
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text (simple frequency-based)
        
        Args:
            text: Text to analyze
            top_n: Number of keywords to return
            
        Returns:
            List of keywords
        """
        # Clean and tokenize
        text = self.clean_text(text.lower())
        words = text.split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'them', 'their'
        }
        
        words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequencies
        word_freq: Dict[str, int] = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Return top N
        keywords = [word for word, _ in sorted_words[:top_n]]
        
        return keywords
    
    def summarize_text(self, text: str, max_sentences: int = 3) -> str:
        """
        Create a simple extractive summary
        
        Args:
            text: Text to summarize
            max_sentences: Number of sentences in summary
            
        Returns:
            Summary text
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', self.clean_text(text))
        
        if len(sentences) <= max_sentences:
            return text
        
        # Simple approach: take first and last sentences, plus one from middle
        if max_sentences == 1:
            return sentences[0]
        elif max_sentences == 2:
            return f"{sentences[0]} {sentences[-1]}"
        else:
            mid_idx = len(sentences) // 2
            selected = [sentences[0], sentences[mid_idx], sentences[-1]]
            return ' '.join(selected[:max_sentences])
    
    def batch_process_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Process multiple documents in batch
        
        Args:
            documents: List of document dicts with keys:
                - id, title, content, doc_type, and optional metadata
        
        Returns:
            List of all (chunk_text, metadata) tuples from all documents
        """
        all_chunks = []
        
        for doc in documents:
            try:
                chunks = self.process_document(
                    doc_id=doc["id"],
                    title=doc["title"],
                    content=doc["content"],
                    doc_type=doc["doc_type"],
                    category=doc.get("category"),
                    applicable_makes=doc.get("applicable_makes"),
                    applicable_models=doc.get("applicable_models"),
                    year_from=doc.get("year_from"),
                    year_to=doc.get("year_to")
                )
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Failed to process document {doc.get('id')}: {e}")
                continue
        
        logger.info(f"Batch processed {len(documents)} documents into {len(all_chunks)} total chunks")
        return all_chunks
