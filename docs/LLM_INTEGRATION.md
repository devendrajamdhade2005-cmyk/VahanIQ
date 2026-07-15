# LLM Integration Documentation

## Overview

The AutoSense AI platform uses Large Language Models (LLMs) to generate plain-language repair guides from ML predictions and RAG-retrieved context. The system supports both Anthropic Claude and OpenAI GPT.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Complete AI Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌─────┐ │
│  │  Sensor  │──→   │    ML    │──→   │   RAG    │──→   │ LLM │ │
│  │   Data   │      │ Predictor│      │ Context  │      │     │ │
│  └──────────┘      └──────────┘      └──────────┘      └─────┘ │
│       ↓                  ↓                  ↓              ↓     │
│  OBD-II 25+        XGBoost 5-class    FAISS Search    Claude/  │
│  parameters        Failure Types      Knowledge+Cases   GPT     │
│  Time-series       SHAP Explain       Semantic Search  Guide    │
│                                                                   │
│  Output: Complete Diagnosis with Actionable Repair Guide        │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. LLM Service (`llm_service.py`)

Handles all LLM interactions with support for multiple providers.

**Features**:
- Multi-provider support (Claude, GPT)
- Repair guide generation
- Customer-friendly summaries
- Cost estimation
- Structured JSON output parsing
- Fallback handling

**Methods**:

#### `generate_repair_guide()`
```python
repair_guide = await llm_service.generate_repair_guide(
    vehicle_info={
        "make": "Tata",
        "model": "Nexon",
        "year": 2022,
        "mileage": 45000,
        "registration_number": "MH01AB1234"
    },
    ml_prediction={
        "failure_type": "brake",
        "probability": 0.85,
        "severity": "critical",
        "explanation": "Brake pads critically worn..."
    },
    rag_context={
        "knowledge_articles": [...],
        "similar_cases": [...]
    },
    diagnosis_description="Customer reports squealing noise"
)
```

**Output Structure**:
```json
{
  "diagnosis_summary": "Brief issue summary",
  "root_cause": "Most likely cause",
  "urgency": "immediate|urgent|moderate|low",
  "repair_steps": [
    {
      "step_number": 1,
      "title": "Step title",
      "description": "Detailed instructions",
      "safety_warning": "Optional warning",
      "estimated_time_minutes": 15
    }
  ],
  "required_parts": [
    {
      "part_name": "Front brake pad set",
      "part_number": "5801517959",
      "quantity": 1,
      "estimated_cost_inr": 2500,
      "priority": "critical|recommended|optional"
    }
  ],
  "required_tools": ["19mm socket", "C-clamp", "Jack stands"],
  "estimated_labor_hours": 2.5,
  "estimated_total_cost_inr": 8500,
  "safety_precautions": ["Wear safety glasses", ...],
  "quality_checks": ["Test brake pedal feel", ...],
  "common_mistakes": ["Don't compress caliper with bleeder closed", ...],
  "additional_notes": "Bed in new pads properly",
  "metadata": {
    "generated_at": "2024-01-15T10:30:00Z",
    "llm_provider": "anthropic",
    "llm_model": "claude-3-sonnet-20240229",
    "ml_confidence": 0.85,
    "rag_articles_used": 3,
    "similar_cases_used": 2
  }
}
```

#### `generate_diagnosis_summary()`
Customer-friendly explanation (2-3 sentences)
```python
summary = await llm_service.generate_diagnosis_summary(
    vehicle_info={...},
    sensor_data={...},
    ml_prediction={...}
)
# "Your brake pads are worn and need replacement soon. This is a common 
# issue after 40,000-50,000 km and should be addressed within the next 
# week to ensure safe braking."
```

#### `generate_cost_estimate()`
Detailed cost breakdown
```python
cost = await llm_service.generate_cost_estimate(
    failure_type="brake",
    vehicle_info={...},
    rag_context={...}
)
```

### 2. Diagnosis Service (`diagnosis_service.py`)

Orchestrates the complete diagnosis flow.

**Main Method**: `create_diagnosis()`

**Flow**:
1. **Load Vehicle + Sensor Data**: Get latest OBD-II readings
2. **ML Prediction**: XGBoost failure classification
3. **RAG Retrieval**: Semantic search for context
4. **LLM Generation**: Create repair guide (if confidence > 30%)
5. **Save to DB**: Store diagnosis with all results
6. **Return Complete Package**: All components unified

**Usage**:
```python
from app.services.diagnosis_service import get_diagnosis_service

diagnosis_service = get_diagnosis_service()

result = await diagnosis_service.create_diagnosis(
    db=db,
    vehicle_id=42,
    current_user=mechanic_user,
    notes="Customer reports brake noise",
    generate_repair_guide=True
)
```

**Methods**:
- `create_diagnosis()` - Full diagnosis flow
- `get_diagnosis_details()` - Retrieve saved diagnosis
- `regenerate_repair_guide()` - Regenerate with new notes

## API Endpoints

### POST `/api/diagnoses/`
Create new AI diagnosis

**Request**:
```json
{
  "vehicle_id": 42,
  "notes": "Customer reports squealing noise during braking",
  "generate_repair_guide": true
}
```

**Response**: `CompleteDiagnosisResponse`
```json
{
  "diagnosis": {
    "id": 15,
    "vehicle_id": 42,
    "failure_type": "brake",
    "confidence_score": 0.85,
    "severity": "critical",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "vehicle": {...},
  "ml_prediction": {...},
  "rag_context": {
    "knowledge_articles_count": 3,
    "similar_cases_count": 2,
    "knowledge_articles": [...],
    "similar_cases": [...]
  },
  "repair_guide": {
    "diagnosis_summary": "...",
    "repair_steps": [...],
    "required_parts": [...],
    "estimated_total_cost_inr": 8500,
    "estimated_labor_hours": 2.5
  },
  "customer_summary": "Your brake pads are worn...",
  "sensor_data_timestamp": "2024-01-15T09:45:00Z"
}
```

### GET `/api/diagnoses/`
List diagnoses with filters

**Query Parameters**:
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 50, max: 100)
- `vehicle_id`: Filter by vehicle
- `failure_type`: Filter by type (brake, engine, fuel, electrical)
- `severity`: Filter by severity (critical, high, medium, low)
- `status`: Filter by status (pending, in_progress, completed, cancelled)

### GET `/api/diagnoses/{diagnosis_id}`
Get diagnosis details

**Query Parameters**:
- `include_full_context`: Include complete RAG context (default: false)

### PUT `/api/diagnoses/{diagnosis_id}`
Update diagnosis

**Request**:
```json
{
  "description": "Updated notes",
  "status": "in_progress",
  "mechanic_feedback": "Confirmed brake pad wear",
  "accuracy_rating": 5
}
```

### POST `/api/diagnoses/{diagnosis_id}/regenerate-guide`
Regenerate repair guide

**Request**:
```json
{
  "custom_notes": "Customer wants premium brake pads"
}
```

**Response**: Updated `RepairGuide`

### GET `/api/diagnoses/stats/overview`
Get diagnosis statistics

**Query Parameters**:
- `days`: Analysis period (default: 30, max: 365)

**Response**:
```json
{
  "total_diagnoses": 150,
  "by_failure_type": {
    "brake": 45,
    "engine": 30,
    "fuel": 25,
    "electrical": 20,
    "normal": 30
  },
  "by_severity": {
    "critical": 25,
    "high": 40,
    "medium": 50,
    "low": 35
  },
  "by_status": {
    "pending": 30,
    "in_progress": 45,
    "completed": 70,
    "cancelled": 5
  },
  "average_confidence": 0.78,
  "accuracy_stats": {
    "feedback_count": 80,
    "average_rating": 4.5
  }
}
```

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# LLM Provider Selection
LLM_PROVIDER=anthropic  # or "openai"

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-api03-...
LLM_MODEL=claude-3-sonnet-20240229  # or claude-3-opus, claude-3-haiku

# OpenAI (GPT)
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4  # or gpt-3.5-turbo, gpt-4-turbo
```

### Model Selection

**Anthropic Claude**:
- `claude-3-opus-20240229` - Most capable, best reasoning (expensive)
- `claude-3-sonnet-20240229` - Balanced performance/cost (recommended)
- `claude-3-haiku-20240307` - Fast, economical

**OpenAI GPT**:
- `gpt-4` - High quality, slower
- `gpt-4-turbo` - Fast GPT-4
- `gpt-3.5-turbo` - Economical, good quality

**Recommendation**: Use `claude-3-sonnet-20240229` for best balance of quality, speed, and cost.

## Prompt Engineering

### Repair Guide Prompt Structure

```
You are an expert automotive technician creating a detailed repair guide.

VEHICLE INFORMATION:
- Vehicle: [make] [model] ([year])
- Mileage: [km]
- Registration: [number]

AI DIAGNOSIS:
- Failure Type: [type]
- Confidence: [%]
- Severity: [level]
- ML Explanation: [explanation]
- Mechanic's Notes: [notes]

RELEVANT REPAIR MANUALS:
[Top 3 knowledge articles with content excerpts]

SIMILAR PAST CASES:
[Top 3 similar repair cases with resolutions]

TASK:
Generate comprehensive step-by-step repair guide...

OUTPUT FORMAT (JSON):
[Structured JSON schema]
```

**Key Prompt Elements**:
1. **Role Definition**: "Expert automotive technician"
2. **Context**: Vehicle info, ML prediction, RAG context
3. **Task**: Clear instruction for repair guide
4. **Format**: Strict JSON output specification
5. **Temperature**: 0.3 (consistent, less creative)

### Customization

To customize prompts, edit methods in `llm_service.py`:
- `_build_repair_guide_prompt()` - Main repair guide
- `_build_diagnosis_summary_prompt()` - Customer summary
- `_build_cost_estimate_prompt()` - Cost estimation

## Testing

### Complete Pipeline Test

```bash
cd /Users/devendra/Desktop/VahanIQ
python ml/scripts/test_complete_ai_pipeline.py
```

This tests:
1. ML prediction from sensor data
2. RAG context retrieval
3. LLM repair guide generation
4. Database persistence
5. Complete response structure

### Manual API Testing

```bash
# 1. Login to get token
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "mechanic.mumbai@autosense.ai", "password": "mechanic123"}'

# 2. Create diagnosis
curl -X POST "http://localhost:8000/api/diagnoses/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": 1,
    "notes": "Customer reports brake squealing",
    "generate_repair_guide": true
  }'

# 3. Get diagnosis details
curl -X GET "http://localhost:8000/api/diagnoses/1?include_full_context=true" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Regenerate guide
curl -X POST "http://localhost:8000/api/diagnoses/1/regenerate-guide" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"custom_notes": "Use premium brake pads"}'
```

## Performance

**Latency Breakdown**:
- ML Prediction: 50-100ms
- RAG Retrieval: 50-100ms
- LLM Generation: 2-5 seconds (varies by model)
- **Total**: ~3-6 seconds for complete diagnosis

**Optimization Tips**:
1. Use faster LLM models (Haiku, GPT-3.5-turbo) for lower latency
2. Cache RAG context for repeated queries
3. Generate repair guide asynchronously for instant response
4. Implement request queuing for high load

## Cost Estimation

**Per Diagnosis** (approximate):

**Anthropic Claude Sonnet**:
- Input tokens: ~2000 tokens (context)
- Output tokens: ~1000 tokens (guide)
- Cost: $0.009 per diagnosis

**OpenAI GPT-4**:
- Input tokens: ~2000 tokens
- Output tokens: ~1000 tokens
- Cost: $0.045 per diagnosis

**OpenAI GPT-3.5-turbo**:
- Cost: $0.003 per diagnosis

**Monthly Estimate** (1000 diagnoses):
- Claude Sonnet: ~$9/month
- GPT-4: ~$45/month
- GPT-3.5-turbo: ~$3/month

## Error Handling

**LLM Failures**:
- API key missing: Service initialization fails gracefully
- Rate limits: Exponential backoff (implemented by SDK)
- JSON parsing errors: Fallback to default structure
- Timeout: 30-second timeout per request

**Fallback Behavior**:
```python
if repair_guide is None:
    # Continue without LLM guide
    # Diagnosis still created with ML + RAG only
    # Customer summary not generated
```

## Best Practices

### 1. Prompt Quality
- Include specific vehicle details
- Provide ML confidence level
- Add mechanic notes for context
- Reference DTC codes when available

### 2. Context Management
- Limit RAG results to top 3-5 articles
- Include most similar cases
- Balance context length vs. cost

### 3. Output Validation
- Verify JSON structure
- Check required fields
- Validate cost/time estimates
- Ensure safety warnings present

### 4. User Experience
- Generate customer summary separately
- Show progress indicators (ML → RAG → LLM)
- Allow guide regeneration with custom notes
- Collect mechanic feedback for improvement

### 5. Monitoring
- Track LLM response times
- Monitor token usage
- Log API errors
- Measure repair guide accuracy (feedback)

## Troubleshooting

### Issue: "LLM service not initialized"
**Solution**: Check API key in `.env`
```bash
# Anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...

# OpenAI
OPENAI_API_KEY=sk-...
```

### Issue: "JSON parsing failed"
**Cause**: LLM didn't return valid JSON
**Solution**: 
- Check prompt structure
- Increase temperature (0.1-0.5)
- Try different model
- Fallback structure used automatically

### Issue: "Repair guide too generic"
**Solutions**:
- Include more specific RAG context
- Add detailed mechanic notes
- Reference DTC codes
- Use more capable model (Opus, GPT-4)

### Issue: High latency
**Solutions**:
- Use faster model (Haiku, GPT-3.5-turbo)
- Reduce max_tokens
- Generate guide asynchronously
- Cache frequent queries

## Future Enhancements

1. **Multi-language Support**: Hindi repair guides
2. **Image Generation**: Diagram annotations
3. **Voice Output**: Audio repair instructions
4. **Fine-tuning**: Domain-specific model training
5. **Confidence Calibration**: Adjust based on feedback
6. **Interactive Guides**: Follow-up questions
7. **Video Integration**: Link to repair videos
8. **Parts Availability**: Real-time inventory check

## Resources

- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [JSON Schema Validation](https://json-schema.org/)
