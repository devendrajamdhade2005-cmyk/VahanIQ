# AutoSense AI - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Prerequisites
- Python 3.10+ installed
- Node.js 18+ and npm installed
- PostgreSQL or SQLite ready

---

## Step 1: Backend Setup (2 minutes)

```bash
# Navigate to backend directory
cd /Users/devendra/Desktop/VahanIQ/backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed initial data (creates test users, showrooms, vehicles)
python seed_data.py

# Start the backend server
uvicorn app.main:app --reload
```

**Backend is now running at**: `http://localhost:8000`  
**API Docs available at**: `http://localhost:8000/docs`

---

## Step 2: Frontend Setup (1 minute)

Open a **new terminal window**:

```bash
# Navigate to frontend directory
cd /Users/devendra/Desktop/VahanIQ/frontend

# Dependencies are already installed, just start the dev server
npm run dev
```

**Frontend is now running at**: `http://localhost:5173`

---

## Step 3: Login and Test (1 minute)

1. **Open browser**: `http://localhost:5173`
2. **Click any Quick Login button**:
   - **Admin** - See full system management
   - **Mechanic** - Run AI diagnoses
   - **Manager** - View showroom dashboard (coming soon)
   - **Owner** - View vehicle health (coming soon)

3. **Test AI Diagnosis** (Mechanic Dashboard):
   - Select a vehicle from dropdown
   - Click "Run Diagnosis"
   - Wait 3-6 seconds for AI pipeline
   - Click "View Details" to see:
     - ML predictions with SHAP explanations
     - RAG context (articles + similar cases)
     - LLM-generated repair guide

---

## Test Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@autosense.ai | admin123 |
| Manager | manager.mumbai@autosense.ai | manager123 |
| Mechanic | mechanic.mumbai@autosense.ai | mechanic123 |
| Owner | owner@example.com | owner123 |

---

## Troubleshooting

### Backend Issues

**Problem**: `ModuleNotFoundError`
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Database connection error
```bash
# Solution: Check .env file or create one
cp .env.example .env
# Edit .env with your database credentials
```

**Problem**: Port 8000 already in use
```bash
# Solution: Use a different port
uvicorn app.main:app --reload --port 8001
# Then update frontend .env: VITE_API_BASE_URL=http://localhost:8001
```

### Frontend Issues

**Problem**: `Cannot GET /`
```bash
# Solution: Make sure backend is running first
```

**Problem**: CORS errors in browser console
```bash
# Solution: Backend CORS is already configured for localhost:5173
# If using different port, update backend/app/main.py origins list
```

**Problem**: Login fails with 401
```bash
# Solution: Make sure seed_data.py was run to create test users
cd backend
python seed_data.py
```

---

## Optional: Generate Synthetic Data

To test with more realistic data:

```bash
cd /Users/devendra/Desktop/VahanIQ/ml/scripts

# Generate 50 vehicles with sensor data
python generate_synthetic_data.py

# Load sample repair manuals into knowledge base
python load_knowledge_base.py

# Train ML model (requires sensor data)
python train_prediction_model.py

# Test the complete AI pipeline
python test_complete_ai_pipeline.py
```

---

## Next Steps

### For Development
1. Read `docs/PROJECT_STRUCTURE.md` - Understand the codebase
2. Read `docs/AUTHENTICATION.md` - Auth system details
3. Read `docs/LLM_INTEGRATION.md` - AI pipeline explained
4. Read `docs/RAG_PIPELINE.md` - Knowledge retrieval system

### For Production
1. Set up proper PostgreSQL database
2. Configure environment variables (`.env`)
3. Set up LLM API keys (Anthropic Claude or OpenAI GPT)
4. Run `npm run build` in frontend
5. Deploy backend with Gunicorn or similar
6. Deploy frontend to Vercel/Netlify/similar

---

## File Structure Quick Reference

```
VahanIQ/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   ├── core/              # Config, security, database
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic
│   │   ├── rag/               # RAG pipeline
│   │   └── ml/                # ML predictor
│   └── main.py                # FastAPI app
│
├── frontend/
│   ├── src/
│   │   ├── pages/             # Dashboard pages
│   │   ├── services/          # API clients
│   │   ├── components/        # Reusable components
│   │   └── contexts/          # React contexts
│   └── App.tsx                # Main routing
│
├── ml/
│   ├── scripts/               # Training & testing
│   └── models/                # Saved ML models
│
└── docs/                      # Documentation
```

---

## API Endpoints Quick Reference

### Auth
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Current user

### Vehicles
- `GET /api/vehicles/` - List vehicles
- `POST /api/vehicles/` - Create vehicle

### Diagnoses (AI Pipeline)
- `POST /api/diagnoses/` - Run AI diagnosis
- `GET /api/diagnoses/` - List diagnoses
- `GET /api/diagnoses/{id}` - Get diagnosis details

### Users (Admin only)
- `GET /api/users/` - List users
- `POST /api/users/` - Create user

### Showrooms (Admin only)
- `GET /api/showrooms/` - List showrooms
- `POST /api/showrooms/` - Create showroom

**Full API documentation**: `http://localhost:8000/docs`

---

## Support

- **Documentation**: See `docs/` folder
- **Master Plan**: `AutoSense_AI_Web_Platform_Master_Plan.md`
- **Frontend Summary**: `FRONTEND_COMPLETION_SUMMARY.md`

---

**Happy Coding! 🚗💨**
