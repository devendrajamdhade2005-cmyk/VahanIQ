"""
Load sample repair manuals into knowledge base and build vector index
"""

import sys
import os
import asyncio

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db_session
from app.models.knowledge import KnowledgeDocument
from app.rag.retrieval_service import get_retrieval_service

# Import sample data
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../data'))
from sample_repair_manuals import REPAIR_MANUALS


async def load_knowledge_documents(db: AsyncSession):
    """Load repair manuals into database"""
    print("Loading repair manuals into database...")
    
    # Check if documents already exist
    result = await db.execute(select(KnowledgeDocument))
    existing_docs = result.scalars().all()
    
    if existing_docs:
        print(f"Found {len(existing_docs)} existing documents in database")
        response = input("Do you want to clear and reload? (yes/no): ")
        if response.lower() == 'yes':
            for doc in existing_docs:
                await db.delete(doc)
            await db.commit()
            print("Cleared existing documents")
        else:
            print("Skipping document load")
            return len(existing_docs)
    
    # Add new documents
    loaded_count = 0
    for manual_data in REPAIR_MANUALS:
        doc = KnowledgeDocument(
            title=manual_data["title"],
            doc_type=manual_data["doc_type"],
            category=manual_data["category"],
            content=manual_data["content"],
            applicable_makes=manual_data["applicable_makes"],
            applicable_models=manual_data["applicable_models"],
            year_from=manual_data["year_from"],
            year_to=manual_data["year_to"],
            is_active=True,
            is_verified=True,
            version="1.0"
        )
        
        db.add(doc)
        loaded_count += 1
        print(f"  ✓ Added: {doc.title}")
    
    await db.commit()
    print(f"\nLoaded {loaded_count} repair manuals into database")
    return loaded_count


async def build_vector_index(db: AsyncSession):
    """Build FAISS vector index from knowledge base"""
    print("\nBuilding vector index...")
    
    retrieval_service = get_retrieval_service()
    
    # Initialize and index
    stats = await retrieval_service.index_knowledge_base(db=db, rebuild=True)
    
    print(f"\nVector Index Statistics:")
    print(f"  - Documents indexed: {stats['indexed']}")
    print(f"  - Total chunks: {stats['chunks']}")
    print(f"  - Timestamp: {stats['timestamp']}")
    
    return stats


async def test_retrieval(db: AsyncSession):
    """Test retrieval with sample queries"""
    print("\n" + "="*60)
    print("TESTING RETRIEVAL SERVICE")
    print("="*60)
    
    retrieval_service = get_retrieval_service()
    await retrieval_service.initialize()
    
    test_queries = [
        {
            "query": "brake pad replacement procedure",
            "vehicle_make": "Tata",
            "vehicle_model": "Nexon"
        },
        {
            "query": "engine overheating coolant temperature",
            "vehicle_make": "Tata",
            "vehicle_model": "Harrier"
        },
        {
            "query": "fuel trim running lean vacuum leak",
            "vehicle_make": "Tata",
            "vehicle_model": None
        },
        {
            "query": "low battery voltage alternator charging",
            "vehicle_make": "Tata",
            "vehicle_model": None
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {test['query']}")
        if test['vehicle_make']:
            print(f"   Vehicle: {test['vehicle_make']} {test['vehicle_model'] or '(all models)'}")
        
        results = await retrieval_service.search_knowledge(
            query=test["query"],
            top_k=3,
            vehicle_make=test["vehicle_make"],
            vehicle_model=test["vehicle_model"]
        )
        
        print(f"   Results: {len(results)} found")
        
        for j, result in enumerate(results, 1):
            print(f"\n   Result {j}:")
            print(f"   - Title: {result['title']}")
            print(f"   - Type: {result['doc_type']} | Category: {result['category']}")
            print(f"   - Similarity: {result['similarity']:.3f}")
            print(f"   - Preview: {result['content'][:150]}...")
    
    # Test vector store stats
    print("\n" + "="*60)
    stats = retrieval_service.get_vector_store_stats()
    print("Vector Store Statistics:")
    for key, value in stats.items():
        print(f"  - {key}: {value}")


async def main():
    """Main execution"""
    print("="*60)
    print("AUTOSENSE AI - KNOWLEDGE BASE LOADER")
    print("="*60)
    
    try:
        # Get database session
        async with get_db_session() as db:
            # Load documents
            doc_count = await load_knowledge_documents(db)
            
            # Build vector index
            stats = await build_vector_index(db)
            
            # Test retrieval
            if doc_count > 0 or stats['indexed'] > 0:
                await test_retrieval(db)
            
            print("\n" + "="*60)
            print("✓ Knowledge base setup complete!")
            print("="*60)
            print("\nNext steps:")
            print("1. Add more repair manuals and technical bulletins")
            print("2. Integrate with LLM service for repair guide generation")
            print("3. Test with real diagnosis data")
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
