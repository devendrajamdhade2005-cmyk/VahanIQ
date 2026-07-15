# RAG Pipeline Documentation

## Overview

The AutoSense AI platform uses a Retrieval-Augmented Generation (RAG) pipeline to provide mechanics with contextual repair guidance based on:
- Repair manuals and technical bulletins
- Similar past repair cases
- Vehicle-specific knowledge

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RAG Pipeline                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │   Document   │──→   │   Vector     │──→   │  FAISS    │ │
│  │  Processor   │      │   Store      │      │  Index    │ │
│  └──────────────┘      └──────────────┘      └───────────┘ │
│         ↓                     ↓                      ↓       │
│  Chunking 500w         Sentence-BERT          L2 Distance   │
│  Overlap 50w          all-MiniLM-L6-v2       Similarity     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Retrieval Service                         │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • Search Knowledge Base                             │   │
│  │  • Find Similar Cases                                │   │
│  │  • Get Repair Context (Combined)                     │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Vector Store (`vector_store.py`)

**Technology**: FAISS (Facebook AI Similarity Search)

**Embedding Model**: `all-MiniLM-L6-v2`
- Dimension: 384
- Fast and lightweight
- Optimized for semantic search

**Features**:
- Singleton pattern for single model load
- Persistent storage (FAISS index + metadata)
- Batch embedding generation
- Filtered search by document type, category, vehicle

**Usage**:
```python
from app.rag.vector_store import VectorStore

store = VectorStore()
store.initialize()

# Add documents
texts = ["Brake pad replacement procedure...", ...]
metadata = [{"doc_id": 1, "category": "brake"}, ...]
doc_ids = store.add_documents(texts, metadata)

# Search
results = store.search(
    query="brake pad wear symptoms",
    top_k=5,
    filters={"category": "brake"}
)

# Persist
store.save()
```

### 2. Document Processor (`document_processor.py`)

**Chunking Strategy**:
- Target chunk size: 500 words
- Overlap: 50 words (10%)
- Minimum chunk: 50 words
- Sentence-aware splitting (preserves context)

**Text Cleaning**:
- Normalize whitespace
- Remove special characters
- Standardize quotes
- Preserve punctuation

**Metadata Extraction**:
- Content hash (deduplication)
- Word/character counts
- Document ID and chunk index
- Vehicle applicability
- Category and type
- Timestamp

**Usage**:
```python
from app.rag.document_processor import DocumentProcessor

processor = DocumentProcessor(
    chunk_size=500,
    chunk_overlap=50
)

# Process document
chunks = processor.process_document(
    doc_id=1,
    title="Brake System Guide",
    content="Full manual text...",
    doc_type="manual",
    category="brake",
    applicable_makes="Tata",
    applicable_models="Nexon,Harrier"
)

# Returns: [(chunk_text, metadata), ...]
```

### 3. Retrieval Service (`retrieval_service.py`)

High-level interface combining vector search with database queries.

**Key Methods**:

#### `search_knowledge()`
Semantic search over knowledge base
```python
results = await retrieval_service.search_knowledge(
    query="brake pad replacement cost",
    top_k=5,
    doc_type="manual",
    category="brake",
    vehicle_make="Tata",
    vehicle_model="Nexon"
)
```

Returns:
```json
[
  {
    "content": "Brake pad replacement procedure...",
    "title": "Tata Nexon Brake Guide",
    "doc_type": "manual",
    "category": "brake",
    "similarity": 0.87,
    "doc_id": 1,
    "chunk_index": 3
  }
]
```

#### `find_similar_cases()`
Find past repair cases with similar symptoms
```python
cases = await retrieval_service.find_similar_cases(
    db=db,
    diagnosis_text="Squealing noise during braking",
    failure_type="brake",
    vehicle_make="Tata",
    vehicle_model="Nexon",
    top_k=5
)
```

Returns:
```json
[
  {
    "repair_case_id": 42,
    "failure_type": "brake",
    "description": "Brake pad worn",
    "resolution_notes": "Replaced front brake pads",
    "cost": 3500.0,
    "duration_hours": 1.5,
    "similarity": 0.92
  }
]
```

#### `get_repair_context()`
Combined knowledge + cases for comprehensive guidance
```python
context = await retrieval_service.get_repair_context(
    db=db,
    failure_type="brake",
    diagnosis_description="Squealing noise, reduced braking",
    vehicle_make="Tata",
    vehicle_model="Nexon",
    dtc_codes=["C0035", "C0040"]
)
```

Returns:
```json
{
  "query": "brake failure: Squealing noise... C0035 C0040",
  "knowledge_articles": [...],
  "similar_cases": [...],
  "vehicle": {"make": "Tata", "model": "Nexon"},
  "failure_type": "brake",
  "retrieved_at": "2024-01-15T10:30:00"
}
```

## API Endpoints

### POST `/api/knowledge/search`
Semantic search over knowledge base

**Request**:
```json
{
  "query": "brake pad replacement procedure",
  "top_k": 5,
  "doc_type": "manual",
  "category": "brake",
  "vehicle_make": "Tata",
  "vehicle_model": "Nexon"
}
```

**Response**:
```json
{
  "query": "brake pad replacement procedure",
  "results": [
    {
      "content": "Brake System Maintenance...",
      "title": "Tata Nexon Brake Guide",
      "doc_type": "manual",
      "category": "brake",
      "similarity": 0.87,
      "doc_id": 1,
      "chunk_index": 2,
      "metadata": {...}
    }
  ],
  "total_results": 5,
  "search_time_ms": 42.5
}
```

### POST `/api/knowledge/similar-cases`
Find similar repair cases

**Request**:
```json
{
  "diagnosis_text": "Squealing noise during braking, reduced efficiency",
  "failure_type": "brake",
  "vehicle_make": "Tata",
  "vehicle_model": "Nexon",
  "top_k": 5
}
```

**Response**:
```json
{
  "results": [
    {
      "repair_case_id": 42,
      "failure_type": "brake",
      "description": "Brake pad wear",
      "resolution_notes": "Replaced front brake pads",
      "cost": 3500.0,
      "duration_hours": 1.5,
      "similarity": 0.92,
      "case_text": "brake - Brake pad wear..."
    }
  ],
  "total_results": 3
}
```

### POST `/api/knowledge/repair-context`
Get comprehensive repair context

**Request**:
```json
{
  "failure_type": "brake",
  "diagnosis_description": "Squealing noise during braking",
  "vehicle_make": "Tata",
  "vehicle_model": "Nexon",
  "dtc_codes": ["C0035", "C0040"]
}
```

**Response**: Combined knowledge articles + similar cases

### GET `/api/knowledge/stats`
Get vector store statistics

**Response**:
```json
{
  "total_documents": 150,
  "dimension": 384,
  "model": "all-MiniLM-L6-v2",
  "index_path": "app/rag/indices/faiss_index",
  "metadata_count": 450
}
```

### POST `/api/knowledge/index/rebuild`
Rebuild vector index (Admin only)

**Request**:
```json
{
  "rebuild": true
}
```

**Response**:
```json
{
  "indexed": 5,
  "total": 5,
  "chunks": 45,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Knowledge Document CRUD

- `GET /api/knowledge/documents` - List documents
- `GET /api/knowledge/documents/{id}` - Get document
- `POST /api/knowledge/documents` - Create document (Admin)
- `PUT /api/knowledge/documents/{id}` - Update document (Admin)
- `DELETE /api/knowledge/documents/{id}` - Soft delete (Admin)

## Loading Knowledge Base

### 1. Load Sample Manuals

```bash
cd /Users/devendra/Desktop/VahanIQ
python ml/scripts/load_knowledge_base.py
```

This script:
1. Loads 5 sample repair manuals into database
2. Processes documents into chunks
3. Generates embeddings
4. Builds FAISS index
5. Tests retrieval with sample queries

### 2. Sample Manuals Included

1. **Tata Nexon Brake System** (brake category)
   - Inspection procedures
   - Pad replacement
   - Common issues and DTC codes
   - Parts and pricing

2. **Engine Cooling System** (engine category)
   - Overheating diagnosis
   - Thermostat testing
   - Coolant specifications
   - Common failures

3. **Fuel System Troubleshooting** (fuel category)
   - Fuel trim analysis
   - Lean/rich running
   - EVAP system
   - Injector diagnosis

4. **Electrical System** (electrical category)
   - Battery and charging
   - Voltage diagnostics
   - Starter issues
   - Alternator testing

5. **Maintenance Schedule** (maintenance category)
   - Periodic service intervals
   - Consumables pricing
   - Seasonal maintenance

## Configuration

Add to `.env`:
```bash
# RAG Settings
RAG_INDEX_PATH=app/rag/indices/faiss_index
RAG_EMBEDDINGS_MODEL=all-MiniLM-L6-v2
RAG_TOP_K_RESULTS=5
```

## Performance

**Embedding Generation**:
- Single text: ~10ms
- Batch (50 texts): ~200ms

**Search**:
- Query embedding: ~10ms
- FAISS search: ~1-5ms
- Total latency: 15-50ms

**Index Size**:
- 5 manuals → 45 chunks
- Index file: ~100 KB
- Metadata file: ~50 KB

## Best Practices

### 1. Document Quality
- Use clear, structured text
- Include technical specifications
- Add DTC code references
- Specify vehicle applicability
- Keep procedures step-by-step

### 2. Chunking Strategy
- 500 words balances context and specificity
- 50-word overlap preserves meaning across boundaries
- Sentence-aware prevents mid-sentence splits

### 3. Search Optimization
- Combine failure type + symptoms in query
- Include DTC codes when available
- Filter by vehicle make/model
- Use category filters

### 4. Metadata
- Tag documents with vehicle applicability
- Use consistent categories
- Version control for updates
- Mark verified content

### 5. Index Management
- Rebuild index after bulk document updates
- Save index after significant changes
- Monitor index size and performance
- Archive old/superseded documents

## Future Enhancements

1. **Advanced Embeddings**
   - Fine-tune model on automotive domain
   - Multi-language support (Hindi)
   - Image embedding for diagrams

2. **Hybrid Search**
   - Combine semantic + keyword search
   - BM25 for exact matches
   - Rerank with cross-encoder

3. **Document Processing**
   - PDF extraction
   - Image OCR
   - Table parsing
   - Diagram recognition

4. **Smart Filtering**
   - Year-based applicability
   - Part availability
   - Regional variations
   - Warranty considerations

5. **Analytics**
   - Search query analysis
   - Click-through rates
   - Content gaps
   - User feedback

## Troubleshooting

### Issue: "Model not found"
```bash
# Download model manually
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: "Index not found"
```bash
# Rebuild index
python ml/scripts/load_knowledge_base.py
```

### Issue: Poor search results
- Check document relevance
- Verify vehicle filters
- Increase top_k
- Review chunk quality
- Add more training data

### Issue: Slow search
- Check index size
- Monitor embedding model load
- Use batch operations
- Consider GPU acceleration

## Example Integration

```python
from app.rag.retrieval_service import get_retrieval_service

# In diagnosis endpoint
async def create_diagnosis(vehicle_id, failure_type, description):
    # ... ML prediction ...
    
    # Get repair context
    retrieval_service = get_retrieval_service()
    context = await retrieval_service.get_repair_context(
        db=db,
        failure_type=failure_type,
        diagnosis_description=description,
        vehicle_make=vehicle.make,
        vehicle_model=vehicle.model,
        dtc_codes=dtc_codes
    )
    
    # Pass to LLM for guide generation
    repair_guide = await generate_repair_guide(context)
    
    return diagnosis
```

## Resources

- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Semantic Search Guide](https://www.sbert.net/examples/applications/semantic-search/README.html)
