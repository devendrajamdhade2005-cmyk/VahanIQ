"""
Test complete AI pipeline: ML + RAG + LLM
Tests the full diagnosis flow end-to-end
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db_session
from app.models.vehicle import Vehicle
from app.models.user import User
from app.services.diagnosis_service import get_diagnosis_service


async def test_diagnosis_pipeline():
    """Test complete diagnosis pipeline"""
    
    print("="*80)
    print("AUTOSENSE AI - COMPLETE PIPELINE TEST")
    print("Testing: ML Prediction → RAG Context → LLM Guide Generation")
    print("="*80)
    
    async with get_db_session() as db:
        # 1. Get a test vehicle (should have sensor data)
        print("\n1. Loading test vehicle...")
        query = select(Vehicle).limit(1)
        result = await db.execute(query)
        vehicle = result.scalar_one_or_none()
        
        if not vehicle:
            print("❌ No vehicles found. Please run seed_data.py first.")
            return
        
        print(f"   ✓ Vehicle: {vehicle.make} {vehicle.model} ({vehicle.year})")
        print(f"   ✓ Registration: {vehicle.registration_number}")
        print(f"   ✓ Mileage: {vehicle.mileage} km")
        print(f"   ✓ Health: {vehicle.health_status}")
        
        # 2. Get a mechanic user
        print("\n2. Loading mechanic user...")
        query = select(User).where(User.role == "mechanic").limit(1)
        result = await db.execute(query)
        mechanic = result.scalar_one_or_none()
        
        if not mechanic:
            print("❌ No mechanic user found. Please run seed_data.py first.")
            return
        
        print(f"   ✓ Mechanic: {mechanic.full_name}")
        print(f"   ✓ Email: {mechanic.email}")
        
        # 3. Run complete diagnosis
        print("\n3. Running AI diagnosis pipeline...")
        print("   → Step 1: ML prediction from sensor data")
        print("   → Step 2: RAG context retrieval")
        print("   → Step 3: LLM repair guide generation")
        
        diagnosis_service = get_diagnosis_service()
        
        try:
            result = await diagnosis_service.create_diagnosis(
                db=db,
                vehicle_id=vehicle.id,
                current_user=mechanic,
                notes="Test diagnosis - checking brake system",
                generate_repair_guide=True
            )
            
            print("\n" + "="*80)
            print("✓ DIAGNOSIS COMPLETE")
            print("="*80)
            
            # 4. Display results
            diagnosis = result["diagnosis"]
            ml_pred = result["ml_prediction"]
            rag_ctx = result["rag_context"]
            repair_guide = result.get("repair_guide")
            customer_summary = result.get("customer_summary")
            
            print(f"\n📊 DIAGNOSIS SUMMARY")
            print(f"   Diagnosis ID: {diagnosis['id']}")
            print(f"   Failure Type: {diagnosis['failure_type'].upper()}")
            print(f"   Confidence: {diagnosis['confidence_score']*100:.1f}%")
            print(f"   Severity: {diagnosis['severity'].upper()}")
            print(f"   Status: {diagnosis['status']}")
            
            print(f"\n🤖 ML PREDICTION")
            print(f"   Type: {ml_pred['failure_type']}")
            print(f"   Probability: {ml_pred['probability']*100:.1f}%")
            print(f"   Severity: {ml_pred['severity']}")
            print(f"   Explanation: {ml_pred['explanation'][:200]}...")
            
            print(f"\n📚 RAG CONTEXT")
            print(f"   Knowledge Articles: {rag_ctx['knowledge_articles_count']}")
            print(f"   Similar Cases: {rag_ctx['similar_cases_count']}")
            
            if rag_ctx['knowledge_articles']:
                print(f"\n   Top Articles:")
                for i, article in enumerate(rag_ctx['knowledge_articles'][:2], 1):
                    print(f"   {i}. {article['title']}")
                    print(f"      Similarity: {article['similarity']:.3f}")
                    print(f"      Preview: {article['content'][:100]}...")
            
            if rag_ctx['similar_cases']:
                print(f"\n   Similar Cases:")
                for i, case in enumerate(rag_ctx['similar_cases'][:2], 1):
                    print(f"   {i}. Case #{case['repair_case_id']}")
                    print(f"      Type: {case['failure_type']}")
                    print(f"      Cost: ₹{case.get('cost', 0):.2f}")
                    print(f"      Duration: {case.get('duration_hours', 0):.1f}h")
                    print(f"      Similarity: {case['similarity']:.3f}")
            
            if customer_summary:
                print(f"\n👤 CUSTOMER SUMMARY")
                print(f"   {customer_summary}")
            
            if repair_guide:
                print(f"\n🔧 REPAIR GUIDE")
                print(f"   Summary: {repair_guide['diagnosis_summary']}")
                print(f"   Root Cause: {repair_guide['root_cause']}")
                print(f"   Urgency: {repair_guide['urgency'].upper()}")
                print(f"   Estimated Cost: ₹{repair_guide['estimated_total_cost_inr']:,.2f}")
                print(f"   Estimated Time: {repair_guide['estimated_labor_hours']:.1f} hours")
                
                print(f"\n   Repair Steps ({len(repair_guide['repair_steps'])} total):")
                for step in repair_guide['repair_steps'][:3]:
                    print(f"   {step['step_number']}. {step['title']}")
                    print(f"      {step['description'][:100]}...")
                    print(f"      Time: {step['estimated_time_minutes']} minutes")
                    if step.get('safety_warning'):
                        print(f"      ⚠️  {step['safety_warning']}")
                
                if repair_guide['required_parts']:
                    print(f"\n   Required Parts ({len(repair_guide['required_parts'])} total):")
                    for part in repair_guide['required_parts'][:3]:
                        print(f"   • {part['part_name']}")
                        print(f"     Qty: {part['quantity']} | Cost: ₹{part['estimated_cost_inr']:,.2f} | Priority: {part['priority']}")
                
                if repair_guide['required_tools']:
                    print(f"\n   Required Tools:")
                    for tool in repair_guide['required_tools'][:5]:
                        print(f"   • {tool}")
                
                if repair_guide['safety_precautions']:
                    print(f"\n   ⚠️  Safety Precautions:")
                    for precaution in repair_guide['safety_precautions'][:3]:
                        print(f"   • {precaution}")
                
                # Metadata
                if repair_guide.get('metadata'):
                    meta = repair_guide['metadata']
                    print(f"\n   📈 Generation Metadata:")
                    print(f"   LLM Provider: {meta.get('llm_provider', 'N/A')}")
                    print(f"   LLM Model: {meta.get('llm_model', 'N/A')}")
                    print(f"   ML Confidence: {meta.get('ml_confidence', 0)*100:.1f}%")
                    print(f"   Articles Used: {meta.get('rag_articles_used', 0)}")
                    print(f"   Cases Used: {meta.get('similar_cases_used', 0)}")
            
            print("\n" + "="*80)
            print("✓ PIPELINE TEST SUCCESSFUL")
            print("="*80)
            print("\nThe AI system successfully:")
            print("  1. Analyzed sensor data with ML model")
            print("  2. Retrieved relevant repair context from knowledge base")
            print("  3. Generated actionable repair guide with LLM")
            print("  4. Saved diagnosis to database")
            print(f"\nDiagnosis ID: {diagnosis['id']} - Ready for mechanic review")
            
        except Exception as e:
            print(f"\n❌ Pipeline test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


async def main():
    """Main execution"""
    try:
        await test_diagnosis_pipeline()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Check if LLM API key is set
    from app.core.config import settings
    
    if settings.LLM_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
        print("\n⚠️  Warning: ANTHROPIC_API_KEY not set in .env")
        print("   LLM repair guide generation will fail.")
        print("   Set ANTHROPIC_API_KEY in backend/.env to enable full pipeline.\n")
    elif settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
        print("\n⚠️  Warning: OPENAI_API_KEY not set in .env")
        print("   LLM repair guide generation will fail.")
        print("   Set OPENAI_API_KEY in backend/.env to enable full pipeline.\n")
    
    asyncio.run(main())
