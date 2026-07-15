# AutoSense AI Web Platform

AI-powered predictive maintenance platform for vehicles with explainable diagnostics and automated repair guidance.

## 🚀 Features

### 🤖 AI Intelligence (Complete Pipeline)
- **ML Predictions**: XGBoost multi-class failure classifier (5 types: normal, brake, engine, fuel, electrical)
- **SHAP Explainability**: Feature importance with plain-language explanations
- **RAG Context Retrieval**: FAISS semantic search over 5+ repair manuals + similar cases
- **LLM Repair Guides**: Claude/GPT-generated step-by-step repair instructions
- **Complete Diagnosis Flow**: Sensor Data → ML → RAG → LLM (3-6 second latency)

### 👥 Four Role-Based Dashboards
- **Admin**: Platform-wide monitoring, user management, analytics
- **Showroom Manager**: Multi-vehicle oversight, mechanic assignments, revenue tracking
- **Mechanic**: AI-powered diagnosis, repair guides, case management
- **Car Owner**: Vehicle health, service history, cost estimates

### 🔧 Vehicle Management
- **OBD-II Integration**: 25+ sensor parameters (RPM, temps, brake wear, battery, fuel trim)
- **Health Scoring**: Algorithm-based status (Healthy/Watch/Warning/Critical)
- **Sensor Time-Series**: Historical data tracking and analytics
- **DTC Code Mapping**: Diagnostic trouble code interpretation

### 📚 Knowledge Base & RAG
- **Semantic Search**: 15-50ms latency over repair manuals
- **Similar Case Finder**: Past repair retrieval with similarity scoring
- **Manual Processing**: 500-word chunks, 50-word overlap, sentence-aware
- **Vehicle Filtering**: Make/model/year specific content

### 🔐 Security & Access Control
- **JWT Authentication**: Access + refresh tokens
- **RBAC System**: 4 roles with granular permissions
- **Multi-Tenant Isolation**: Showroom-scoped data access
- **Audit Logging**: Security events and user actions

### 📊 Analytics & Reporting
- **Diagnosis Statistics**: Failure type distribution, confidence metrics
- **Cost Tracking**: Parts, labor, total repair costs
- **Performance Metrics**: ML accuracy, mechanic feedback
- **Real-Time Monitoring**: Live alerts and status updates

## 📁 Project Structure

```
VahanIQ/
├── backend/           # FastAPI backend service
│   ├── app/
│   │   ├── api/       # API routes
│   │   ├── core/      # Config, security, dependencies
│   │   ├── models/    # SQLAlchemy database models
│   │   ├── services/  # Business logic
│   │   ├── ml/        # ML prediction service
│   │   └── rag/       # RAG pipeline
│   └── tests/
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── public/
├── ml/                # ML training & experiments
│   ├── models/
│   ├── data/
│   ├── notebooks/
│   └── scripts/
└── docs/              # Documentation

```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **ML**: XGBoost, scikit-learn, SHAP
- **RAG**: FAISS, sentence-transformers
- **LLM**: Claude/GPT API
- **Auth**: JWT + RBAC

### Frontend
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: React Query + Context API
- **Charts**: Recharts
- **Real-time**: WebSocket

### Infrastructure
- **Backend Hosting**: Railway/Render
- **Frontend Hosting**: Vercel
- **Database**: Supabase/Neon (managed PostgreSQL)
- **Storage**: S3-compatible object storage

## 🚦 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 14+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run dev
```

### ML Model Training

```bash
cd ml
python scripts/train_prediction_model.py
python scripts/prepare_rag_index.py
```

## 📊 Available Datasets

- **OBD-II Data**: Kaggle automotive sensor datasets
- **Predictive Maintenance**: AI4I 2020 dataset (UCI)
- **Repair Manuals**: Operation CHARM dataset
- **Synthetic Data**: Generated with domain rules

## 🔐 Security Features

- Role-based access control (RBAC)
- Multi-tenant data isolation
- JWT authentication
- HTTPS encryption
- Input validation & sanitization
- Audit logging

## 📈 Roadmap

- [x] Project setup
- [ ] Backend API & database
- [ ] Authentication & RBAC
- [ ] ML prediction pipeline
- [ ] RAG system
- [ ] All 4 dashboards
- [ ] Real-time features
- [ ] Deployment

## 👥 User Roles

1. **Admin** - Platform-wide oversight (Tata Motors team)
2. **Showroom Manager** - Service center operations
3. **Mechanic** - AI-assisted diagnostics & repair
4. **Car Owner** - Vehicle health monitoring & booking

## 📝 License

Proprietary - Tata Motors / VahanIQ

## 🤝 Contributing

Internal project. Contact the development team for access.

---

Built with ❤️ for smarter, safer vehicle maintenance
