# Machine Learning Components

This directory contains ML model training scripts, notebooks, and data generation tools.

## Directory Structure

```
ml/
├── data/              # Dataset storage
│   ├── raw/          # Original datasets (Kaggle, Operation CHARM)
│   ├── processed/    # Preprocessed training data
│   └── synthetic/    # Generated synthetic data
├── models/           # Trained model files
│   ├── failure_prediction_model.pkl
│   └── shap_explainer.pkl
├── notebooks/        # Jupyter notebooks for experiments
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   └── 03_rag_testing.ipynb
└── scripts/          # Training and data generation scripts
    ├── generate_synthetic_data.py
    ├── train_prediction_model.py
    └── prepare_rag_index.py
```

## Synthetic Data Generation

### Quick Start

```bash
# From the VahanIQ root directory
cd ml/scripts

# Generate default dataset (50 vehicles)
python generate_synthetic_data.py

# Generate custom number of vehicles
python generate_synthetic_data.py --vehicles 100
```

### Prerequisites

1. **Database must be initialized:**
   ```bash
   cd ../../backend
   python init_db.py
   python seed_data.py
   ```

2. **Backend dependencies installed:**
   ```bash
   cd ../../backend
   pip install -r requirements.txt
   ```

### What Gets Generated

The script creates realistic synthetic data including:

#### Vehicles (default: 50)
- Tata Motors models: Nexon, Harrier, Safari, Punch, Altroz, Tiago, Tigor
- Realistic variants and colors
- Indian registration numbers (e.g., MH01AB1234)
- Year range: 2018-2024
- Mileage: 8,000-15,000 km per year
- Health status based on age and mileage

#### Vehicle Owners
- One owner per vehicle
- Indian names and phone numbers
- Valid email addresses
- Credentials: `owner123` for all test owners

#### Sensor Readings (~100 per vehicle)
- Distributed over last 30 days
- 25+ OBD-II parameters:
  - Engine: RPM, speed, load, temperatures
  - Fuel: pressure, level, trim values
  - Brakes: pad thickness (4 wheels), fluid pressure
  - Transmission: temperature, gear position
  - Electrical: battery voltage
  - Diagnostics: DTC codes

#### Realistic Patterns

**Driving Patterns:**
- 70% readings during driving
- 30% readings during idle
- Speed ranges: 20-100 km/h (driving), 0 (idle)
- RPM ranges: 1000-4000 (driving), 700-900 (idle)

**Wear Patterns:**
- Brake pads: Wear ~0.2mm per 10,000 km
  - Start: 12mm (new)
  - Critical: <2.5mm
- Battery degradation: Voltage drops after 80,000 km
- Coolant temperature: Normal 85-95°C

**Fault Scenarios (10% of readings):**
- **Brake Issues**: Worn pads (<2.5mm), DTC codes C0035-C0050
- **Engine Issues**: Overheating (>100°C), DTC codes P0300-P0420
- **Fuel Issues**: Trim out of range, DTC codes P0171-P0442
- **Electrical Issues**: Low voltage (<12.5V), DTC codes B0001-U0100

### Health Status Calculation

Vehicles are assigned health status based on mileage and age:

| Mileage | Age | Status |
|---------|-----|--------|
| <30k km | <3 years | Healthy (Green) |
| <60k km | <5 years | Healthy/Watch (Green/Yellow) |
| <100k km | <7 years | Watch/Warning (Yellow/Orange) |
| >100k km | >7 years | Warning/Critical (Orange/Red) |

Health score: 100 - (mileage/1000 × 0.05) - (age × 2)

### Example Output

```
🌱 Generating synthetic data...
✅ Found 2 showrooms
👥 Generating 50 vehicle owners...
🚗 Generating 50 vehicles...
📊 Generating sensor readings...
   Processed 10/50 vehicles...
   Processed 20/50 vehicles...
   Processed 30/50 vehicles...
   Processed 40/50 vehicles...
   Processed 50/50 vehicles...

✨ Synthetic data generation complete!
   Created: 50 owners
   Created: 50 vehicles
   Created: ~5000 sensor readings
```

### Verification

After generation, verify the data:

```bash
# Check vehicles in database
cd ../../backend
python -c "
import asyncio
from app.core.database import async_session_maker
from sqlalchemy import select, func
from app.models.vehicle import Vehicle
from app.models.sensor import SensorReading

async def check():
    async with async_session_maker() as db:
        # Count vehicles
        result = await db.execute(select(func.count(Vehicle.id)))
        vehicle_count = result.scalar()
        print(f'Vehicles: {vehicle_count}')
        
        # Count sensor readings
        result = await db.execute(select(func.count(SensorReading.id)))
        sensor_count = result.scalar()
        print(f'Sensor readings: {sensor_count}')

asyncio.run(check())
"
```

### Use Cases

**For Testing APIs:**
```bash
# Start backend
cd ../../backend
uvicorn app.main:app --reload

# Test endpoints at http://localhost:8000/api/docs
```

**For ML Model Training:**
```python
# Use generated data to train prediction models
python scripts/train_prediction_model.py
```

**For Demo/Presentation:**
- Realistic vehicle fleet across multiple showrooms
- Various failure scenarios
- Time-series sensor data for charts

### Customization

To modify the generation:

1. **Add more Tata models**: Edit `TATA_MODELS` in script
2. **Change failure rate**: Adjust `random.random() < 0.1` (10% fault rate)
3. **Modify wear patterns**: Edit `_apply_wear_patterns()` method
4. **Different time range**: Change `days_ago = random.randint(0, 30)`

### Troubleshooting

**Error: "No showrooms found"**
- Run `python seed_data.py` first to create showrooms

**Error: "ModuleNotFoundError"**
- Ensure you're running from `ml/scripts` directory
- Backend dependencies must be installed

**Database errors:**
- Check DATABASE_URL in backend/.env
- Ensure PostgreSQL is running
- Run `python init_db.py` to create tables

## Next Steps

After generating synthetic data:

1. **Train ML Model**: `python scripts/train_prediction_model.py`
2. **Test Predictions**: `python scripts/test_predictions.py`
3. **Prepare RAG Index**: `python scripts/prepare_rag_index.py`
4. **Test APIs**: Use Postman/Swagger with generated data
5. **Build Frontend**: Connect to populated backend

## ML Model Training

### Quick Start

```bash
# From ml/scripts directory
python train_prediction_model.py
```

### What It Does

The training script:
1. **Loads sensor data** from database
2. **Labels failures** based on thresholds:
   - Brake: pad thickness < 2.5mm
   - Engine: coolant temp > 100°C
   - Fuel: trim values > ±10%
   - Electrical: battery voltage < 12.5V
   - Normal: everything else
3. **Trains XGBoost** classifier
4. **Creates SHAP explainer** for interpretability
5. **Saves model** to `ml/models/`

### Model Architecture

**Algorithm**: XGBoost (Gradient Boosting)
- Multi-class classification (5 classes)
- 20 sensor features
- Handles missing values
- Built-in feature importance

**Features Used**:
- Engine: rpm, speed, load, temperatures, MAF
- Fuel: pressure, level, trim values
- Brakes: pad thickness (4 wheels), fluid pressure
- Electrical: battery voltage, O2 sensor
- Other: transmission temp, mileage

**Output**:
- Failure type (normal/brake/engine/fuel/electrical)
- Probability (0-1)
- SHAP values for explainability
- Top contributing features

### Explainability (SHAP)

SHAP (SHapley Additive exPlanations) provides:
- **Feature importance**: Which sensors matter most
- **Individual predictions**: Why this specific prediction
- **Plain language**: Human-readable explanations

Example:
```
"Brake failure risk is high (85% probability). 
Front brake pads are critically worn (FL: 1.8mm, FR: 2.1mm). 
Replace brake pads immediately."
```

### Testing Predictions

After training, test the model:

```bash
python test_predictions.py
```

This will:
- Load real sensor data from database
- Make predictions for 10 vehicles
- Show failure type, probability, severity
- Display plain-language explanations
- Test edge cases (critical scenarios)

### Model Files

After training, these files are created in `ml/models/`:

- `failure_prediction_model.pkl` - Trained XGBoost model
- `scaler.pkl` - Feature scaler (StandardScaler)
- `shap_explainer.pkl` - SHAP explainer
- `feature_names.pkl` - Feature list
- `model_metadata.pkl` - Training metadata

### Integration with Backend

The model is loaded automatically by the backend:

```python
from app.ml.predictor import predict_failure

# Make prediction
sensor_data = {
    'rpm': 2500,
    'coolant_temp': 95,
    'brake_pad_thickness_fl': 2.0,
    # ... other sensors
}

result = predict_failure(sensor_data)
# Returns: failure_type, probability, explanation, etc.
```

### Expected Performance

With synthetic data:
- **Accuracy**: ~85-95% (depends on failure distribution)
- **Precision**: High for critical failures (brake, engine)
- **Recall**: Balanced across all failure types

Real-world performance will vary based on:
- Data quality
- Sensor calibration
- Failure label accuracy

### Retraining

To retrain with new data:

1. Generate/collect more sensor readings
2. Run training script again
3. Model automatically reloads in backend (on restart)

For production:
- Retrain monthly with mechanic feedback
- Use actual failure outcomes as labels
- A/B test new models before deployment

## Data Sources (Future)

When ready for production:

- **Real OBD-II Data**: Kaggle datasets or Tata fleet data
- **Repair Manuals**: Operation CHARM database
- **Historical Repairs**: Actual service center records
- **Expert Labels**: Mechanic-verified failure classifications


---

## Knowledge Base and RAG Pipeline

The platform uses a Retrieval-Augmented Generation (RAG) system for contextual repair guidance.

### Setup Knowledge Base

1. **Load Sample Repair Manuals**:
```bash
python ml/scripts/load_knowledge_base.py
```

This will:
- Load 5 comprehensive repair manuals into database
- Process documents into 500-word chunks with 50-word overlap
- Generate embeddings using Sentence-BERT
- Build FAISS vector index for semantic search
- Test retrieval with sample queries

### Sample Manuals Included

1. **Tata Nexon Brake System Maintenance** - Complete brake service guide
2. **Engine Cooling System Diagnosis** - Overheating troubleshooting
3. **Fuel System Troubleshooting** - Fuel trim analysis and EVAP
4. **Electrical System Diagnosis** - Battery and charging systems
5. **General Maintenance Schedule** - Periodic service intervals

### Vector Store

- **Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Index**: FAISS L2 distance
- **Storage**: `backend/app/rag/indices/`
- **Search Speed**: 15-50ms per query
- **Persistent**: Index saved to disk after build

### Usage Examples

```python
from app.rag.retrieval_service import get_retrieval_service

# Initialize service
retrieval_service = get_retrieval_service()
await retrieval_service.initialize()

# Search knowledge base
results = await retrieval_service.search_knowledge(
    query="brake pad replacement Tata Nexon",
    top_k=5,
    vehicle_make="Tata",
    vehicle_model="Nexon"
)

# Find similar cases
cases = await retrieval_service.find_similar_cases(
    db=db,
    diagnosis_text="Squealing noise during braking",
    failure_type="brake",
    vehicle_make="Tata",
    top_k=5
)

# Get comprehensive repair context
context = await retrieval_service.get_repair_context(
    db=db,
    failure_type="brake",
    diagnosis_description="Brake warning light, squealing noise",
    vehicle_make="Tata",
    vehicle_model="Nexon",
    dtc_codes=["C0035", "C0040"]
)
```

### API Endpoints

- `POST /api/knowledge/search` - Semantic search over manuals
- `POST /api/knowledge/similar-cases` - Find similar repair cases
- `POST /api/knowledge/repair-context` - Combined knowledge + cases
- `GET /api/knowledge/stats` - Vector store statistics
- `POST /api/knowledge/index/rebuild` - Rebuild index (admin only)
- `GET /api/knowledge/documents` - List knowledge documents
- `POST /api/knowledge/documents` - Add new document (admin)

### Adding Custom Manuals

1. **Via API** (Recommended):
```bash
curl -X POST "http://localhost:8000/api/knowledge/documents" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tata Punch Suspension Guide",
    "doc_type": "manual",
    "category": "suspension",
    "content": "Your manual content here...",
    "applicable_makes": "Tata",
    "applicable_models": "Punch",
    "year_from": 2021,
    "year_to": 2024,
    "is_active": true,
    "is_verified": true
  }'
```

2. **Via Python Script**:
```python
# Add to ml/data/sample_repair_manuals.py
REPAIR_MANUALS.append({
    "title": "Your Manual Title",
    "doc_type": "manual",
    "category": "brake",
    "applicable_makes": "Tata",
    "applicable_models": "Nexon,Harrier",
    "year_from": 2018,
    "year_to": 2024,
    "content": """
    Your detailed manual content here...
    """
})
```

Then reload:
```bash
python ml/scripts/load_knowledge_base.py
```

### Performance

**Embedding Generation**:
- Single text: ~10ms
- Batch (50 texts): ~200ms
- Model size: ~80MB

**Search Performance**:
- Query embedding: ~10ms
- FAISS search (1000 docs): ~1-5ms
- Post-filtering: ~1-2ms
- Total latency: **15-50ms**

**Storage**:
- 5 manuals → 45 chunks
- FAISS index: ~100 KB
- Metadata: ~50 KB

### Verification

After loading, verify the system:

```bash
# Check vector store stats
curl -X GET "http://localhost:8000/api/knowledge/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test search
curl -X POST "http://localhost:8000/api/knowledge/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "brake pad replacement procedure",
    "top_k": 3,
    "vehicle_make": "Tata",
    "vehicle_model": "Nexon"
  }'
```

See `docs/RAG_PIPELINE.md` for comprehensive documentation.
