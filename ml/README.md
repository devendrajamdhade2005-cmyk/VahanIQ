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
2. **Prepare RAG Index**: `python scripts/prepare_rag_index.py`
3. **Test APIs**: Use Postman/Swagger with generated data
4. **Build Frontend**: Connect to populated backend

## Data Sources (Future)

When ready for production:

- **Real OBD-II Data**: Kaggle datasets or Tata fleet data
- **Repair Manuals**: Operation CHARM database
- **Historical Repairs**: Actual service center records
- **Expert Labels**: Mechanic-verified failure classifications
